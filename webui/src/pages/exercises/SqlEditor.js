import { useRef } from 'react';
import Editor from '@monaco-editor/react';

const SqlEditor = ({ onChange, }) => {
    const editorRef = useRef(null);

    const handleEditorDidMount = (editor, monaco) => {
        editorRef.current = editor;

        // Set the default language to SQL
        monaco.languages.register({ id: 'sql' });

        // Focus the editor, allowing the user to start typing immediately
        editorRef.current.focus();
    };

    const handleEditorChange = (value) => {
        onChange(value);
    };

    return (
        <div style={{
            backgroundColor: '#1E1E1E',
            padding: '10px 0',
            borderRadius: 12,
            boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
        }}>
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
