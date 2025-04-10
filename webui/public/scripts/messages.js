let CHAT_ID = 0;

class Message {
    constructor(content, is_from_assistant, chat) {
        this.content = content;
        this.is_from_assistant = is_from_assistant;
        this.chat = chat;
        this.msg_id = chat.last_message_id() + 1;
        this.feedback = null;

        this.html = $('<div></div>')
            .addClass('messagebox')
            .addClass(is_from_assistant ? 'messagebox-assistant' : 'messagebox-user');
            
        if (is_from_assistant)
            this.html.append(ICON_ASSISTANT);

        let message = $('<div></div>')
            .addClass('message')
            .html(content);
        
        this.html.append(message);

        if (is_from_assistant) {
            let feedback = $('<div></div>')
                .addClass('message-feedback');

            let feedback_up = $('<span></span>')
                .addClass('feedback-up')
                .html('<i class="fas fa-thumbs-up"></i>');

            let feedback_down = $('<span></span>')
                .addClass('feedback-down')
                .html('<i class="fas fa-thumbs-down"></i>');

            feedback.append(feedback_up);
            feedback.append(feedback_down);

            message.append(feedback);
        }
            
        if (!is_from_assistant)
            this.html.append(ICON_USER);
    }

    set_feedback(feedback) {
        this.feedback = feedback;
    }

    remove() {
        this.html.remove();
    }
}

class Chat {
    constructor(query, query_id, content) {
        CHAT_ID += 1;
        this.id = CHAT_ID;
        this.query = query;
        this.query_id = query_id;
        this.content = content;
        this.messages = [];

        this.html = $('<div></div>')
            .addClass('chat')
            .attr('id', `chat-${CHAT_ID}`);

            
        this.add_title();
    }

    last_message_id() {
        if (this.messages.length == 0)
            return 0;
        
        return this.messages[this.messages.length - 1].msg_id;
    }

    show() {
        $('#result').append(this.html);
    }
    
    add_title() {
        let title = $('<div></div>').addClass('chat-title');
        this.html.append(title);
        this.html.append($('<hr></hr>'));

        return title;
    }

    add_message(content, is_from_assistant) {
        let message = new Message(content, is_from_assistant, this);
        this.messages.push(message);
        
        this.html.append(message.html);
        this.html[0].scrollIntoView({ behavior: 'smooth', block: 'start' });

        return message;
    }

    display_content_as_table() {
        let data = JSON.parse(this.content);
    
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
                let text = rows[i][j];
                if (text === null) {
                    text = 'NULL';
                }

                let cell = $('<td></td>').text(text);
                row.append(cell);
            }
            tbody.append(row);
        }
    
        table.append(tbody);
        
        this.html.append(table);
        this.html[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    display_content_as_text() {
        let pre = $('<pre></pre>').text(this.content);
        this.html.append(pre);
        this.html[0].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    show_buttons() {
        // To be implemented in subclasses
    }
}

class UserChat extends Chat {
    constructor(query, query_id, content) {
        super(query, query_id, content);

        this.thiking_message = null;
    }

    add_title() {
        let title = super.add_title();
        let icon = $('<i></i>')
                .addClass('fas fa-user');
            title.append(icon);
            let pre = $('<pre></pre>').text(this.query);
            title.append(pre);

        return title;
    }

    show_buttons() {
        if (this.buttons)
            return;
    
        let buttons = $('<div></div>').addClass('buttons');
        
        this.buttons = buttons;
        this.html.append(buttons);
    }

    add_button(text, onclick) {
        if (!this.buttons)
            return;

        let button = $('<button></button>')
            .addClass('btn btn-primary')
            .text(text)
            .on('click', onclick);
        
        this.buttons.append(button);
    }

    remove_buttons() {
        if (!this.buttons)
            return;

        this.buttons.remove();
        this.buttons = null;
    }

    start_thinking() {
        if (this.thiking_message)
            return;

        this.thiking_message = this.add_message('Thinking...', true);
        this.thiking_message.html.addClass('thinking');
    }

    stop_thinking() {
        if (this.thiking_message) {
            this.thiking_message.remove();
            this.thiking_message = null;
        }
    }
}

class ErrorChat extends UserChat {
    constructor(query, query_id, content) {
        super(query, query_id, content);

        this.html.addClass('error');
    }

    show_buttons() {
        super.show_buttons();

        this.add_button('Explain error', () => {
            let msg = this.add_message('Explain the error', false);
            this.remove_buttons();
            this.start_thinking();
            
            $.ajax({
                url: '/lensql/api/explain-error-message',
                type: 'POST',
                data: {
                    'query_id': JSON.stringify(this.query_id),
                    'exception': JSON.stringify(this.content),
                    'chat_id': JSON.stringify(this.id),
                    'msg_id': JSON.stringify(msg.msg_id),
                },
                success: (response) => {
                    console.log(response);
                    this.stop_thinking();
                    this.add_message(response.answer, true);
                    this.show_buttons();
                },
                error: (error) => {
                    this.stop_thinking();
                    this.add_message('Error: ' + error, true);
                    this.show_buttons();
                }
            });
        });

        this.add_button('Show example', () => {
            this.add_message('Show me a simpler example that can cause this error', false);
            this.remove_buttons();
            this.start_thinking();
        });

        this.add_button('Where to look', () => {
            this.add_message('Locate the error in the code', false);
            this.remove_buttons();
            this.start_thinking();
        });

        this.add_button('Suggest fix', () => {
            this.add_message('Suggest a fix for the error', false);
            this.remove_buttons();
            this.start_thinking();
        });
    }
}

class ResultChat extends UserChat {
    constructor(query, query_id, content) {
        super(query, query_id, content);

        this.html.addClass('success');
    }

    show_buttons() {
        super.show_buttons();

        this.add_button('Describe query', () => {
            this.add_message('Describe what this query does', false);
            this.remove_buttons();
            this.start_thinking();
        });

        this.add_button('Explain query', () => {
            this.add_message('Explain step by step how this query works', false);
            this.remove_buttons();
            this.start_thinking();
        });
    }
}

class BuiltinChat extends Chat {
    constructor(query, query_id, content) {
        super(query, query_id, content);

        this.html.addClass('builtin');
    }

    add_title() {
        let title = super.add_title();
        let icon = $('<i></i>')
                .addClass('fas fa-search');
            title.append(icon);
            title.append('<br/>');
            let span = $('<span></span>').text(this.query);
            title.append(span);

        return title;
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
