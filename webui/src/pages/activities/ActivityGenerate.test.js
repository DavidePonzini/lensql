import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import ActivityGenerate from './ActivityGenerate';
import i18n from '../../i18n';

const mockApiRequest = jest.fn();
const mockLoadUserInfo = jest.fn();
jest.mock('../../hooks/useAuth', () => ({ __esModule: true, default: () => ({ apiRequest: mockApiRequest }) }));
jest.mock('../../hooks/useUserInfo', () => ({ __esModule: true, default: () => ({ loadUserInfo: mockLoadUserInfo }) }));

const options = {
    success: true, ai_generation_credits: 10, activities: [],
    categories: [{ id: 'SYN', name: 'Syntax', description: 'Problems with SQL names and rules.' },
        { id: 'LOG', name: 'Logical', description: 'Queries that answer the wrong question.' }],
    errors: [{ id: 2, name: 'Ambiguous column', category: 'SYN', description: 'Qualify the column with a table name.' },
        { id: 39, name: 'AND instead of OR', category: 'LOG', description: 'Use OR when either condition should match.' }],
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
    expect(screen.getByText('Credits required: 4')).toBeTruthy();
    expect(screen.queryByLabelText('Solution Search Path')).toBeNull();
    mockApiRequest.mockResolvedValueOnce({ success: false, message: 'Test stops before generation' });
    fireEvent.click(screen.getAllByRole('button', { name: 'Generate' })[1]);
    await waitFor(() => expect(mockApiRequest).toHaveBeenCalledWith('/api/activities/generate', 'POST', expect.objectContaining({
        title: 'Practice', dataset_str: null,
        errors: [{ error_id: 2, difficulty: 1, count: 1 }, { error_id: 2, difficulty: 3, count: 3 }],
    })));
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
    mockApiRequest.mockResolvedValueOnce({ success: false, message: 'Test stops before generation' });
    fireEvent.click(screen.getAllByRole('button', { name: 'Generate' })[1]);
    await waitFor(() => expect(mockApiRequest).toHaveBeenCalledWith('/api/activities/generate', 'POST', expect.objectContaining({
        dataset_str: sql, search_path: 'school',
    })));
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
