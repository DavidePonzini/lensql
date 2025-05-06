import SqlMonacoEditor from "./SqlMonaceEditor";

function ListButtons() {
    return (
        <>
            <button class="btn btn-secondary" id="show-search-path">Show Search Path</button>
            <button class="btn btn-secondary" id="list-schemas">List Schemas</button>
            <button class="btn btn-secondary" id="list-tables">List Tables</button>
            <button class="btn btn-primary" id="clear">Clear output</button>
        </>
    );
}

function Query() {
    return (
        <>
            <SqlMonacoEditor id="editor"/>

            <div class="mt-3">
                <button class="btn btn-primary" id="run-query" disabled>Execute</button>
                <ListButtons></ListButtons>
            </div>

            <div class="mt-3">
                <div id="result"></div>
            </div>
        </>
    );
}

export default Query;