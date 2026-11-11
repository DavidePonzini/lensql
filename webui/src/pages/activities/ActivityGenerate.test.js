import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import ActivityGenerate from './ActivityGenerate';
import i18n from '../../i18n';

const { TextDecoder } = require('util');
global.TextDecoder = TextDecoder;
function generationStream(events) {
    let read = false;
    return { getReader: () => ({
        read: async () => {
            if (read) return { done: true };
            read = true;
            return { done: false, value: Buffer.from(events.map(event => JSON.stringify(event)).join('\n') + '\n') };
        },
        releaseLock: jest.fn(),
    }) };
}
const mockApiRequest = jest.fn();
const mockLoadUserInfo = jest.fn();
jest.mock('../../hooks/useAuth', () => ({ __esModule: true, default: () => ({ apiRequest: mockApiRequest }) }));
jest.mock('../../hooks/useUserInfo', () => ({ __esModule: true, default: () => ({ loadUserInfo: mockLoadUserInfo }) }));

const options = {
    success: true, ai_generation_credits: 10, activities: [],
    categories: [{ id: 'SYN', name: 'Syntax', description: 'Problems with SQL names and rules.' },
        { id: 'LOG', name: 'Logical', description: 'Queries that answer the wrong question.' }],
    errors: [{ id: 2, supported: true, name: 'Ambiguous column', category: 'SYN', description: 'Qualify the column with a table name.' },
        { id: 39, supported: true, name: 'AND instead of OR', category: 'LOG', description: 'Use OR when either condition should match.' }],
};

beforeEach(async () => {
    await i18n.changeLanguage('en');
    mockApiRequest.mockReset();
    mockLoadUserInfo.mockReset();
    mockApiRequest.mockResolvedValue(options);
});

async function openGenerator() {
    const refresh = jest.fn();
    render(<ActivityGenerate refresh={refresh} />);
    fireEvent.click(screen.getByRole('button', { name: 'Generate' }));
    await screen.findByLabelText('Activity title');
    return refresh;
}

test('requests easy and hard exercises for the same error and totals all credits', async () => {
    await openGenerator();
    fireEvent.change(screen.getByLabelText('Activity title'), { target: { value: 'Practice' } });
    fireEvent.change(screen.getByLabelText('Ambiguous column — Easy'), { target: { value: '1' } });
    fireEvent.change(screen.getByLabelText('Ambiguous column — Hard'), { target: { value: '3' } });
    expect(screen.getByText('Credits required: 5')).toBeTruthy();
    expect(screen.queryByLabelText('Solution Search Path')).toBeNull();
    mockApiRequest.mockResolvedValueOnce(generationStream([{ success: false, message: 'Test stops before generation' }]));
    fireEvent.click(screen.getAllByRole('button', { name: 'Generate' })[1]);
    await waitFor(() => expect(mockApiRequest).toHaveBeenCalledWith('/api/activities/generate', 'POST', expect.objectContaining({
        title: 'Practice', dataset_str: null,
        errors: [{ error_id: 2, difficulty: 1, count: 1 }, { error_id: 2, difficulty: 3, count: 3 }],
    }), { stream: true }));
});

test('search shows matching categories and explanatory descriptions', async () => {
    await openGenerator();
    fireEvent.change(screen.getByLabelText('Search errors by name, number or description'), { target: { value: '39' } });
    expect(screen.getByText(i18n.t('errors.categories.log.description'))).toBeTruthy();
    expect(screen.getByText(i18n.t('errors.errors.39.description'))).toBeTruthy();
    expect(screen.queryByText('Use OR when either condition should match.')).toBeNull();
    expect(screen.queryByLabelText('Ambiguous column — Easy')).toBeNull();
    expect(screen.getByLabelText(`${i18n.t('errors.errors.39.name')} — Hard`)).toBeTruthy();
});

test('sends supplied dataset SQL and search path', async () => {
    await openGenerator();
    fireEvent.change(screen.getByLabelText('Activity title'), { target: { value: 'Custom practice' } });
    fireEvent.change(screen.getByLabelText('Ambiguous column — Easy'), { target: { value: '1' } });
    fireEvent.click(screen.getByLabelText('Use my own dataset'));
    const sql = 'CREATE TABLE school.item (id int);';
    fireEvent.change(screen.getByLabelText('Dataset SQL'), { target: { value: sql } });
    fireEvent.change(screen.getByLabelText('Solution Search Path'), { target: { value: 'school' } });
    mockApiRequest.mockResolvedValueOnce(generationStream([{ success: false, message: 'Test stops before generation' }]));
    fireEvent.click(screen.getAllByRole('button', { name: 'Generate' })[1]);
    await waitFor(() => expect(mockApiRequest).toHaveBeenCalledWith('/api/activities/generate', 'POST', expect.objectContaining({
        dataset_str: sql, search_path: 'school',
    }), { stream: true }));
});

test('loads uploaded SQL into the editable dataset field', async () => {
    await openGenerator();
    fireEvent.click(screen.getByLabelText('Use my own dataset'));
    const sql = 'CREATE TABLE item (id int); INSERT INTO item VALUES (1);';
    const file = new File([sql], 'practice.sql', { type: 'application/sql' });
    file.text = jest.fn().mockResolvedValue(sql);
    fireEvent.change(screen.getByLabelText('Upload SQL file (optional)'), { target: { files: [file] } });
    await waitFor(() => expect(screen.getByLabelText('Dataset SQL').value).toBe(sql));
});


test('custom dataset uses the same tips and placeholder as activity creation', async () => {
    await openGenerator();
    fireEvent.click(screen.getByLabelText('Use my own dataset'));
    expect(screen.getByLabelText('Dataset SQL').placeholder).toBe(i18n.t('pages.activities.activity_mask.activity_str_placeholder'));
    expect(screen.getByText(i18n.t('pages.activities.activity_mask.tips_title'))).toBeTruthy();
    expect(screen.queryByText(/Exercises will be shuffled/)).toBeNull();
    expect(screen.queryByText(/Include CREATE SCHEMA if needed/)).toBeNull();
});

test('shows live exercise counts and explains failure refunds', async () => {
    await openGenerator();
    fireEvent.change(screen.getByLabelText('Activity title'), { target: { value: 'Practice' } });
    fireEvent.change(screen.getByLabelText('Ambiguous column — Easy'), { target: { value: '2' } });
    let finish;
    let first = true;
    const releaseLock = jest.fn();
    mockApiRequest.mockResolvedValueOnce({ getReader: () => ({
        read: () => {
            if (first) {
                first = false;
                return Promise.resolve({ value: Buffer.from(JSON.stringify({ type: 'progress', stage: 'exercises', completed: 1, failed: 0, total: 2 }) + '\n'), done: false });
            }
            return new Promise(resolve => { finish = resolve; });
        }, releaseLock,
    }) });
    fireEvent.click(screen.getAllByRole('button', { name: 'Generate' })[1]);
    await screen.findByText('Exercises: 1 completed, 0 failed, 2 requested');
    expect(screen.getByRole('progressbar').getAttribute('aria-valuenow')).toBe('50');
    expect(screen.queryByText(/Credits for failed exercises are refunded/)).toBeNull();
    finish({ value: Buffer.from(JSON.stringify({ success: false, message: 'Refunded' }) + '\n'), done: true });
    await screen.findByText('Refunded');
    expect(screen.queryByRole('progressbar')).toBeNull();
});

test('warns when a partial activity is saved and refreshes the balance', async () => {
    const refresh = await openGenerator();
    fireEvent.change(screen.getByLabelText('Activity title'), { target: { value: 'Practice' } });
    fireEvent.change(screen.getByLabelText('Ambiguous column — Easy'), { target: { value: '2' } });
    mockApiRequest.mockResolvedValueOnce(generationStream([
        { type: 'result', success: true, activity_id: 'PARTIAL', generated_count: 1, failed_count: 1 },
    ]));
    fireEvent.click(screen.getAllByRole('button', { name: 'Generate' })[1]);
    await screen.findByText('Activity created with 1 exercises. 1 exercises failed; their credits have been refunded.');
    await waitFor(() => expect(mockLoadUserInfo).toHaveBeenCalled());
    expect(refresh).toHaveBeenCalled();
});

test('unsupported errors remain visible with disabled difficulty inputs', async () => {
    mockApiRequest.mockResolvedValue({ ...options, errors: [
        ...options.errors,
        { id: 3, category: 'SYN', supported: false },
    ] });
    await openGenerator();
    const name = i18n.t('errors.errors.3.name');
    expect(screen.getByLabelText('Hide unsupported errors').checked).toBe(true);
    expect(screen.queryByLabelText(`${name} — Easy`)).toBeNull();
    fireEvent.click(screen.getByLabelText('Hide unsupported errors'));
    for (const difficulty of ['Easy', 'Medium', 'Hard']) {
        expect(screen.getByLabelText(`${name} — ${difficulty}`).disabled).toBe(true);
        expect(screen.getByLabelText(`Ambiguous column — ${difficulty}`).disabled).toBe(false);
    }
    expect(screen.getByText('Not supported for generation')).toBeTruthy();
    fireEvent.change(screen.getByLabelText('Search errors by name, number or description'), { target: { value: name } });
    expect(screen.getByLabelText(`${name} — Easy`).disabled).toBe(true);
});

test('badges errors identified as common in the personal history', async () => {
    mockApiRequest.mockResolvedValue({ ...options, errors: options.errors.map(error => ({
        ...error, is_common: error.id === 2, common_rank: error.id === 2 ? 1 : null,
    })) });
    await openGenerator();
    expect(screen.getAllByText('Your #1 most common error')).toHaveLength(1);
    expect(screen.getByText('Your #1 most common error').title).toBe('One of your five most frequent errors across all activities and all time.');
});

test('top five checkbox filters personal ranks and keeps other filters active', async () => {
    mockApiRequest.mockResolvedValue({ ...options, errors: options.errors.map(error => ({
        ...error, common_rank: error.id === 2 ? 2 : null,
    })) });
    await openGenerator();
    const otherName = i18n.t('errors.errors.39.name');
    expect(screen.getByLabelText('Only show my top 5 errors').checked).toBe(false);
    fireEvent.click(screen.getByLabelText('Only show my top 5 errors'));
    expect(screen.getByText('Your #2 most common error')).toBeTruthy();
    expect(screen.getByLabelText('Ambiguous column — Easy')).toBeTruthy();
    expect(screen.queryByLabelText(`${otherName} — Easy`)).toBeNull();
    fireEvent.click(screen.getByLabelText('Only show my top 5 errors'));
    expect(screen.getByLabelText(`${otherName} — Easy`)).toBeTruthy();
});
