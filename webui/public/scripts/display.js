TMP_CHATS = [];

function display(json_data) {
    let result = $('#result');
    clear_result();
    
    let data = JSON.parse(json_data);
    
    for (let i = 0; i < data.length; i++) {
        let item = data[i];
        let status = item['status'];
        let query = item['query'];
        let is_builtin = item['is_builtin'];
        
        let chat = new Chat(query, is_builtin);
        TMP_CHATS.push(chat);

        if (status === 'exception') {
            chat.display_text(item['message']);
        } else if (status === 'success_data') {
            chat.display_table(item['result']);
        } else if (status === 'success_message') {
            chat.display_text(item['message']);
        } else if (status === 'error') {
            chat.display_text(item['message']);
        } else {
            console.error(item);
        }
    }
}

function clear_result() {
    let result = $('#result');
    result.empty();
}

