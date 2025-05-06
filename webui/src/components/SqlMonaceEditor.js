import React, { useRef } from 'react';
import Editor from '@monaco-editor/react';

const SqlMonacoEditor = () => {
  const editorRef = useRef(null);

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;

    // Optional: Configure SQL language if needed
    monaco.languages.register({ id: 'sql' });
    // monaco.languages.setMonarchTokensProvider('sql', {
    //   tokenizer: {
    //     root: [
    //       [/\b(SELECT|FROM|WHERE|INSERT|INTO|VALUES|UPDATE|SET|DELETE|JOIN|ON|CREATE|TABLE|AS)\b/i, 'keyword'],
    //       [/[a-z_$][\w$]*/, 'identifier'],
    //       [/"[^"]*"/, 'string'],
    //       [/'[^']*'/, 'string'],
    //       [/[0-9]+/, 'number'],
    //     ],
    //   },
    // });
  };

  const handleEditorChange = (value) => {
    console.log('SQL code:', value);
  };

  return (
    <Editor
      height="400px"
      defaultLanguage="sql"
      defaultValue="SELECT * FROM users;"
      theme="vs-dark" // Dark theme
      onMount={handleEditorDidMount}
      onChange={handleEditorChange}
    />
  );
};

export default SqlMonacoEditor;
