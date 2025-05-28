import ButtonModal from '../components/ButtonModal';
import ButtonShowDataset from '../components/ButtonShowDataset';
import useAuth from '../hooks/useAuth';
import { useEffect, useState } from 'react';

// Data placeholder for exercise data
function ExerciseData({ title, setTitle, request, setRequest, datasetId, setDatasetId, answer, setAnswer }) {
    const { apiRequest } = useAuth();
    const [availableDatasets, setAvailableDatasets] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchDatasets() {
            const data = await apiRequest('/api/datasets/list', 'GET');
            setAvailableDatasets(data.data);
            setLoading(false);
        }

        fetchDatasets();
    }
        , []); // eslint-disable-line react-hooks/exhaustive-deps

    return (
        <>
            <div className="mb-3">
                <label className="form-label">Title</label>
                <input type="text" className="form-control" defaultValue={title} onInput={(e) => setTitle(e.target.value)} />
            </div>
            <div className="mb-3">
                <label className="form-label">Request</label>
                <textarea className="form-control" rows="3" defaultValue={request} onInput={(e) => setRequest(e.target.value)}></textarea>
            </div>
            <div className="mb-3">
                <label className="form-label">Dataset</label>
                {loading ? (
                    <p>Loading datasets...</p>
                ) : (
                    <select className="form-select" aria-label="Default select example" onChange={(e) => setDatasetId(e.target.value)} value={datasetId ? datasetId : ''}>
                        <option value=''>None</option>
                        {availableDatasets.map((dataset) => (
                            <option key={dataset.id} value={dataset.id}>
                                {dataset.name}
                            </option>
                        ))}
                    </select>
                )}
            </div>
            <div className="mb-3">
                <label className="form-label">Answer</label>
                <textarea className="form-control" rows="3" defaultValue={answer} onInput={(e) => setAnswer(e.target.value)}></textarea>
            </div>
        </>
    );
}

// Interactive list of students to assign exercises to
function AssignExercise({ exerciseId }) {
    const { apiRequest } = useAuth();
    const [students, setStudents] = useState([]);
    const [selectAll, setSelectAll] = useState(false);

    async function handleAssignExercise(studentId, value) {
        await apiRequest('/api/exercises/assign', 'POST', {
            'exercise_id': exerciseId,
            'student_id': studentId,
            'value': value,
        });

        setStudents((prev) =>
            prev.map((student) =>
                student.username === studentId ? { ...student, is_assigned: value } : student
            )
        );
    }

    async function handleSelectAll(value) {
        setSelectAll(value);
        // Update UI optimistically
        setStudents((prev) =>
            prev.map((student) => ({ ...student, is_assigned: value }))
        );
        // Send requests for all students
        await Promise.all(
            students.map((student) =>
                apiRequest('/api/exercises/assign', 'POST', {
                    'exercise_id': exerciseId,
                    'student_id': student.username,
                    'value': value,
                })
            )
        );
    }

    useEffect(() => {
        async function fetchStudents() {
            const data = await apiRequest(`/api/assignments/students?id=${exerciseId}`, 'GET');
            setStudents(data.students);
            const allAssigned = data.students.length > 0 && data.students.every((s) => s.is_assigned);
            setSelectAll(allAssigned);
        }

        fetchStudents();
    }, [exerciseId]); // eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => {
        const allAssigned = students.length > 0 && students.every((s) => s.is_assigned);
        setSelectAll(allAssigned);
    }, [students]);

    return (
        <div className="mb-3">
            <label className="form-label">Assign to</label>

            {students.length > 0 && (
                <div className="form-check mb-2">
                    <input
                        className="form-check-input"
                        type="checkbox"
                        id="select-all"
                        checked={selectAll}
                        onChange={(e) => handleSelectAll(e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor="select-all">
                        Select All
                    </label>
                </div>
            )}

            {students.map((student) => (
                <div key={student.username} className="form-check">
                    <input
                        className="form-check-input"
                        type="checkbox"
                        checked={student.is_assigned}
                        id={`student-${student.username}`}
                        onChange={(e) => handleAssignExercise(student.username, e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor={`student-${student.username}`}>
                        {student.username}
                    </label>
                </div>
            ))}
        </div>
    );
}

// Button to add a new exercise + modal to fill in the details
function AddExercise({ refreshAssignments }) {
    const { apiRequest } = useAuth();
    const [exerciseTitle, setExerciseTitle] = useState('');
    const [exerciseRequest, setExerciseRequest] = useState('');
    const [exerciseDatasetId, setExerciseDatasetId] = useState('');
    const [exerciseAnswer, setExerciseAnswer] = useState('');

    async function handleAddExercise() {
        await apiRequest('/api/exercises', 'POST', {
            'title': exerciseTitle,
            'request': exerciseRequest,
            'dataset_id': exerciseDatasetId,
            'expected_answer': exerciseAnswer,
        });

        refreshAssignments();
    }
    return (
        <ButtonModal
            className="btn btn-success"
            title="Add Exercise"
            buttonText="Add New Exercise"
            footerButtons={[
                {
                    text: 'Save',
                    variant: 'primary',
                    onClick: handleAddExercise,
                    autoClose: true,
                },
            ]}
        >
            <ExerciseData
                title={exerciseTitle}
                setTitle={setExerciseTitle}
                request={exerciseRequest}
                setRequest={setExerciseRequest}
                datasetId={exerciseDatasetId}
                setDatasetId={setExerciseDatasetId}
                answer={exerciseAnswer}
                setAnswer={setExerciseAnswer}
            />
        </ButtonModal>
    );
}

// A single row in the exercise list + buttons
function ExerciseRow({ exercise, refreshAssignments }) {
    const { apiRequest } = useAuth();

    const exerciseId = exercise.id;
    const exerciseDatasetName = exercise.dataset_name;
    const [exerciseTitle, setExerciseTitle] = useState(exercise.title);
    const [exerciseRequest, setExerciseRequest] = useState(exercise.request);
    const [exerciseDatasetId, setExerciseDatasetId] = useState(exercise.dataset_id);
    const [exerciseAnswer, setExerciseAnswer] = useState(exercise.expected_answer);
    const isAiGenerated = exercise.is_ai_generated;

    async function handleEditExercise() {
        await apiRequest('/api/exercises', 'PUT', {
            'exercise_id': exerciseId,
            'title': exerciseTitle,
            'request': exerciseRequest,
            'dataset_id': exerciseDatasetId,
            'expected_answer': exerciseAnswer,
        });

        refreshAssignments();
    }

    async function handleDeleteExercise() {
        await apiRequest('/api/exercises', 'DELETE', {
            'exercise_id': exerciseId,
        });

        refreshAssignments();
    }

    return (
        <tr key={exerciseId}>
            <td>{exerciseTitle}</td>
            <td>{exerciseRequest}</td>
            <td>{exerciseAnswer}</td>
            <td>{exerciseDatasetName}</td>
            <td>
                <input
                    type="checkbox"
                    className="form-check-input"
                    checked={isAiGenerated}
                    readOnly
                />
            </td>
            <td>
                <ButtonShowDataset
                    datasetId={exerciseDatasetId}
                    className="btn btn-secondary btn-sm me-1 mb-1"
                />

                <ButtonModal
                    className="btn btn-primary btn-sm me-1 mb-1"
                    title="Assign Exercise"
                    buttonText="Assign"
                >
                    <AssignExercise exerciseId={exerciseId} />
                </ButtonModal>

                <ButtonModal
                    className="btn btn-warning btn-sm me-1 mb-1"
                    title="Edit Exercise"
                    buttonText="Edit"
                    footerButtons={[
                        {
                            text: 'Save',
                            variant: 'primary',
                            onClick: handleEditExercise,
                            autoClose: true,
                        },
                    ]}
                >
                    <ExerciseData
                        title={exerciseTitle}
                        setTitle={setExerciseTitle}
                        request={exerciseRequest}
                        setRequest={setExerciseRequest}
                        datasetId={exerciseDatasetId}
                        setDatasetId={setExerciseDatasetId}
                        answer={exerciseAnswer}
                        setAnswer={setExerciseAnswer}
                    />
                </ButtonModal>


                <button className='btn btn-danger btn-sm me-1 mb-1' onClick={handleDeleteExercise}>
                    Delete
                </button>
            </td>
        </tr>
    );
}


// Main page component
function ManageAssignments() {
    const { apiRequest } = useAuth();
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchAssignments = async () => {
        const data = await apiRequest('/api/exercises/list', 'GET');
        setAssignments(data.data);
        setLoading(false);
    };

    useEffect(() => {
        fetchAssignments();
    }, []);     // eslint-disable-line react-hooks/exhaustive-deps

    if (loading) return <p>Loading...</p>;

    return (
        <div className="container mt-4">
            <table className="table table-striped table-hover">
                <thead className="table-dark">
                    <tr>
                        <th>Title</th>
                        <th>Request</th>
                        <th>Answer</th>
                        <th>Dataset</th>
                        <th>AI</th>
                        <th style={{width: '264px'}}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {assignments.map((assignment) => (
                        <ExerciseRow
                            key={assignment.id}
                            exercise={assignment}
                            refreshAssignments={fetchAssignments}
                        />
                    ))}
                </tbody>
                <tfoot>
                    <tr>
                        <td colSpan="6" className="text-center">
                            <AddExercise refreshAssignments={fetchAssignments} />
                        </td>
                    </tr>
                </tfoot>
            </table>
        </div>
    );
}

export default ManageAssignments;