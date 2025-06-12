import useAuth from '../../hooks/useAuth';
import { useEffect, useState } from 'react';
import ExerciseRow from './ExerciseRow';
import AddExercise from './AddExercise';
import Table from 'react-bootstrap/Table';

// Main page component
function ManageAssignments() {
    const { apiRequest } = useAuth();
    const [assignments, setAssignments] = useState([]);
    const [loading, setLoading] = useState(true);

    async function fetchAssignments() {
        const data = await apiRequest('/api/exercises/list', 'GET');
        setAssignments(data.data);
        setLoading(false);
    };

    useEffect(() => {
        fetchAssignments();
    }, []);     // eslint-disable-line react-hooks/exhaustive-deps

    if (loading) return <p>Loading...</p>;

    return (
        <Table striped borderless hover>
            <thead className="table-dark">
                <tr>
                    <th>Title</th>
                    <th>Request</th>
                    <th>Dataset</th>
                    <th>AI</th>
                    <th style={{ width: '353px' }}>Actions</th>
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
        </Table>
    );
}

export default ManageAssignments;