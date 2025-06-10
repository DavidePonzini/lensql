import useAuth from '../../hooks/useAuth';
import ItemAssignmentList from '../../components/ItemAssignmentList';

function AssignStudents({ teacher }) {
    const { apiRequest } = useAuth();

    const fetchStudents = async () => {
        const data = await apiRequest(`/api/admin/students?teacher=${teacher}`, 'GET');
        console.log(data);

        return data.data.map((s) => ({
            id: s.username,
            label: s.username,
            isAssigned: s.is_student,
        }));
    };

    async function assignStudent(student, value) {
        await apiRequest('/api/admin/assign-student', 'POST', {
            student,
            value,
        });
    };

    return (
        <ItemAssignmentList
            fetchItems={fetchStudents}
            assignAction={assignStudent}
            title="Assign to"
        />
    );
}

export default AssignStudents;
