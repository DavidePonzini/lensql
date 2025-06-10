import useAuth from '../../hooks/useAuth';
import { useEffect, useState } from 'react';

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
            const data = await apiRequest(`/api/assignments/students?exercise_id=${exerciseId}`, 'GET');
            setStudents(data.students);
            // const allAssigned = data.students.length > 0 && data.students.every((s) => s.is_assigned);
            // setSelectAll(allAssigned);
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

export default AssignExercise;