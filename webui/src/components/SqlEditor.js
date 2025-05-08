import '../styles/SqlEditor.css';

import React, { useRef } from 'react';
import Editor from '@monaco-editor/react';

const SqlEditor = ({ onChange }) => {
    const editorRef = useRef(null);

    const handleEditorDidMount = (editor, monaco) => {
        editorRef.current = editor;

        monaco.languages.register({ id: 'sql' });
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
