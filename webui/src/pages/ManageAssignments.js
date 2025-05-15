import ButtonModal from '../components/ButtonModal';
import useAuth from '../hooks/useAuth';
import { useEffect, useState } from 'react';

// Data placeholder for exercise data
function ExerciseData({ title, setTitle, request, setRequest, dataset, setDataset, answer, setAnswer }) {
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
                <textarea className="form-control" rows="3" defaultValue={dataset} onInput={(e) => setDataset(e.target.value)}></textarea>
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
        await apiRequest('/api/assign-exercise', 'POST', {
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
                apiRequest('/api/assign-exercise', 'POST', {
                    'exercise_id': exerciseId,
                    'student_id': student.username,
                    'value': value,
                })
            )
        );
    }

    useEffect(() => {
        async function fetchStudents() {
            const data = await apiRequest('/api/get-assignment-students', 'POST', {
                'exercise_id': exerciseId,
            });
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
    const [exerciseDataset, setExerciseDataset] = useState('');
    const [exerciseAnswer, setExerciseAnswer] = useState('');

    async function handleAddExercise() {
        await apiRequest('/api/add-exercise', 'POST', {
            'title': exerciseTitle,
            'request': exerciseRequest,
            'dataset': exerciseDataset,
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
                    label: 'Save',
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
                dataset={exerciseDataset}
                setDataset={setExerciseDataset}
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
    const [exerciseTitle, setExerciseTitle] = useState(exercise.title);
    const [exerciseRequest, setExerciseRequest] = useState(exercise.request);
    const [exerciseDataset, setExerciseDataset] = useState(exercise.dataset);
    const [exerciseAnswer, setExerciseAnswer] = useState(exercise.expected_answer);
    const isAiGenerated = exercise.is_ai_generated;

    async function handleEditExercise() {
        await apiRequest('/api/edit-exercise', 'POST', {
            'exercise_id': exerciseId,
            'title': exerciseTitle,
            'request': exerciseRequest,
            'dataset': exerciseDataset,
            'expected_answer': exerciseAnswer,
        });

        refreshAssignments();
    }

    async function handleDeleteExercise() {
        await apiRequest('/api/delete-exercise', 'POST', {
            'exercise_id': exerciseId,
        });

        refreshAssignments();
    }

    return (
        <tr key={exerciseId}>
            <td>{exerciseTitle}</td>
            <td>{exerciseRequest}</td>
            <td>{exerciseAnswer}</td>
            <td>
                <input
                    type="checkbox"
                    className="form-check-input"
                    checked={isAiGenerated}
                    readOnly
                />
            </td>
            <td>
                <ButtonModal
                    className="btn btn-secondary btn-sm me-1"
                    title="View Dataset"
                    buttonText="Dataset"
                >
                    <pre className="code">
                        {exerciseDataset}
                    </pre>
                </ButtonModal>

                <ButtonModal
                    className="btn btn-primary btn-sm me-1"
                    title="Assign Exercise"
                    buttonText="Assign"
                >
                    <AssignExercise exerciseId={exerciseId} />
                </ButtonModal>

                <ButtonModal
                    className="btn btn-warning btn-sm me-1"
                    title="Edit Exercise"
                    buttonText="Edit"
                    footerButtons={[
                        {
                            label: 'Save',
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
                        dataset={exerciseDataset}
                        setDataset={setExerciseDataset}
                        answer={exerciseAnswer}
                        setAnswer={setExerciseAnswer}
                    />
                </ButtonModal>


                <button className='btn btn-danger btn-sm me-1' onClick={handleDeleteExercise}>
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
        const data = await apiRequest('/api/get-all-exercises');
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
                        <th>AI</th>
                        <th>Actions</th>
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
                        <td colSpan="4" className="text-center">
                            <AddExercise refreshAssignments={fetchAssignments} />
                        </td>
                    </tr>
                </tfoot>
            </table>
        </div>
    );
}

export default ManageAssignments;