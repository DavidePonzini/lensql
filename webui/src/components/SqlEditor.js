import '../styles/SqlEditor.css';

import React, { useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';

const SqlEditor = ({ onChange, onSubmit }) => {
    const editorRef = useRef(null);

    const handleEditorDidMount = (editor, monaco) => {
        editorRef.current = editor;

        // Set the default language to SQL
        monaco.languages.register({ id: 'sql' });

        // Run the query when the user presses Ctrl + Enter
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, onSubmit);

        // Focus the editor, allowing the user to start typing immediately
        editorRef.current.focus();
    };

    const handleEditorChange = (value) => {
        onChange(value);
    };

    return (
        <div className='sql-editor'>
            <Editor
                height="400px"
                defaultLanguage="sql"
                // defaultValue="SELECT * FROM users;"
                theme="vs-dark" // Dark theme
                onMount={handleEditorDidMount}
                onChange={handleEditorChange}
                options={
                    {
                        fontSize: 16,
                        lineNumbers: 'on',
                        minimap: {
                            enabled: false,
                        },
                        // automaticLayout: true,
                        scrollBeyondLastLine: false,
                        wordWrap: 'off',
                    }
                }
            />
        </div>
    );
};

export default SqlEditor;
