function display(json_data) {
    let data = JSON.parse(json_data);
    let status = data['status'];

    if (status === 'error') {
        display_text(data['message']);
        return;
    }
    if (status === 'success') {
        if (data['data']) {
            display_table(data['data']);
            return;
        }
        if (data['affected_rows']) {
            display_text(`Affected rows: ${data['affected_rows']}`);
            return;
        }
    }

    console.warn(data);
}

function display_table(json_data) {
    data = JSON.parse(json_data);

    let columns = data['columns'];
    let row_idx = data['index'];
    let rows = data['data'];

    let result = $('#result');
    result.empty();

    let table = $('<table></table>').addClass('table table-striped table-bordered');
    let thead = $('<thead></thead>');
    let header_row = $('<tr></tr>');
    let header = $('<th></th>').text('Index');
    header_row.append(header);

    for (let i = 0; i < columns.length; i++) {
        let th = $('<th></th>').text(columns[i]);
        header_row.append(th);
    }
    thead.append(header_row);
    table.append(thead);

    let tbody = $('<tbody></tbody>');
    for (let i = 0; i < rows.length; i++) {
        let row = $('<tr></tr>');
        let index_cell = $('<td></td>').text(row_idx[i]);
        row.append(index_cell);

        for (let j = 0; j < rows[i].length; j++) {
            let cell = $('<td></td>').text(rows[i][j]);
            row.append(cell);
        }
        tbody.append(row);
    }

    table.append(tbody);
    result.append(table);
}

function display_text(text) {
    let result = $('#result');
    result.empty();

    let pre = $('<pre></pre>').text(text);
    result.append(pre);
}

function clear_result() {
    let result = $('#result');
    result.empty();
}

