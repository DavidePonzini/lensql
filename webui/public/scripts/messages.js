let CHAT_ID = 0;

class Message {
    constructor(content, is_from_assistant, msg_id) {
        this.content = content;
        this.is_from_assistant = is_from_assistant;
        this.feedback = null;
        this.msg_id = msg_id;

        this.elem = $('<div></div>')
            .addClass('messagebox')
            .addClass(is_from_assistant ? 'messagebox-assistant' : 'messagebox-user')
            .attr('id', `msg-${msg_id}`);
            
        if (is_from_assistant)
            this.elem.append(ICON_ASSISTANT);

        let message = $('<div></div>')
            .addClass('message')
            .html(content);
        
        this.elem.append(message);

        if (is_from_assistant) {
            let feedback = $('<div></div>')
                .addClass('message-feedback')
                .attr('id', `feedback-${msg_id}`);

            let feedback_up = $('<span></span>')
                .addClass('feedback-up')
                .attr('id', `feedback-up-${msg_id}`)
                .html('<i class="fas fa-thumbs-up"></i>');

            let feedback_down = $('<span></span>')
                .addClass('feedback-down')
                .attr('id', `feedback-down-${msg_id}`)
                .html('<i class="fas fa-thumbs-down"></i>');

            feedback.append(feedback_up);
            feedback.append(feedback_down);

            message.append(feedback);
        }
            
        if (!is_from_assistant)
            this.elem.append(ICON_USER);
    }

    set_feedback(feedback) {
        this.feedback = feedback;
    }
}

class Chat {
    constructor(query, is_builtin) {
        CHAT_ID += 1;
        this.id = CHAT_ID;

        this.query = query;
        this.is_builtin = is_builtin;
        
        this.messages = [];

        this.elem = $('<div></div>')
            .addClass('chat')
            .attr('id', `chat-${CHAT_ID}`);

        let title = $('<div></div>').addClass('chat-title');
        if (this.is_builtin) {
            let icon = $('<i></i>')
                .addClass('fas fa-search');
            title.append(icon);
            title.append('<br/>');
            let span = $('<span></span>').text(query);
            title.append(span);
        } else {
            let icon = $('<i></i>')
                .addClass('fas fa-user');
            title.append(icon);
            let pre = $('<pre></pre>').text(query);
            title.append(pre);
        }
        this.elem.append(title);
        this.elem.append($('<hr></hr>'));
        
        $('#result').append(this.elem);
    }

    add_message(content, is_from_assistant) {
        let msg_id = this.messages.length + 1;
        let message = new Message(content, is_from_assistant, msg_id);
        this.messages.push(message);
        
        this.elem.append(message.elem);
        this.elem[0].scrollIntoView({ behavior: 'smooth', block: 'start' });

        return msg_id;
    }

    display_table(json_data) {
        let data = JSON.parse(json_data);
    
        let columns = data['columns'];
        // let row_idx = data['index'];
        let rows = data['data'];
    
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
        
        this.elem.append(table);
        this.elem[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    display_text(text) {
        let pre = $('<pre></pre>').text(text);
        this.elem.append(pre);
        this.elem[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

ICON_USER = `
    <div class="icon">
        <i class="fas fa-user"></i>
        <br>
        You 
    </div>
`

ICON_ASSISTANT = `
    <div class="icon">
        <i class="fas fa-search"></i>
        <br>
        LensQL
    </div>
`
