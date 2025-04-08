function display(json_data) {
    clear_result();
    
    let data = JSON.parse(json_data);
    for (let i = 0; i < data.length; i++) {
        let item = data[i];
        // console.log(item);
        let status = item['status'];

        if (status === 'exception') {
            display_text(item['message']);
        } else if (status === 'success_data') {
            display_table(item['result']);
        } else if (status === 'success_message') {
            display_text(item['message']);
        } else if (status === 'error') {
            display_text(item['message']);
        } else {
            console.error(item);
        }
    }

    $('#result')[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function display_table(json_data) {
    data = JSON.parse(json_data);

    let columns = data['columns'];
    // let row_idx = data['index'];
    let rows = data['data'];

    let result = $('#result');
    // result.empty();

    let table = $('<table></table>').addClass('table table-bordered table-hover table-responsive');
    let thead = $('<thead></thead>').addClass('table-dark');
    let header_row = $('<tr></tr>');
    // let header = $('<th></th>').text('#');
    // header_row.append(header);

    for (let i = 0; i < columns.length; i++) {
        let th = $('<th></th>').text(columns[i]);
        header_row.append(th);
    }
    thead.append(header_row);
    table.append(thead);

    let tbody = $('<tbody></tbody>').addClass('table-group-divider');
    for (let i = 0; i < rows.length; i++) {
        let row = $('<tr></tr>');
        // let index_cell = $('<td></td>').text(row_idx[i]);
        // row.append(index_cell);

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
    // result.empty();

    let pre = $('<pre></pre>').text(text);
    result.append(pre);
}

function clear_result() {
    let result = $('#result');
    result.empty();
}

