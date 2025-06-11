import useAuth from '../../hooks/useAuth';
import ItemAssignmentList from '../../components/ItemAssignmentList';

function AssignDatasets({ teacher }) {
    const { apiRequest } = useAuth();

    const fetchDatasets = async () => {
        const data = await apiRequest(`/api/admin/datasets?teacher=${teacher}`, 'GET');
        console.log(data);

        return data.data.map((s) => ({
            id: s.name,
            label: s.name,
            isAssigned: s.is_assigned,
        }));
    };

    async function assignDataset(dataset, value) {
        await apiRequest('/api/admin/assign-dataset', 'POST', {
            teacher,
            dataset,
            value,
        });
    };

    return (
        <ItemAssignmentList
            fetchItems={fetchDatasets}
            assignAction={assignDataset}
            title="Assign dataset"
        />
    );
}

export default AssignDatasets;
