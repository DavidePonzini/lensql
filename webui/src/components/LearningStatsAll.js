import LearningStatsQueries from "./LearningStatsQueries";
import LearningStatsMessages from "./LearningStatsMessages";
import LearningStatsErrors from "./LearningStatsErrors";

function LearningStatsAll({ classId = null, exerciseId = null, isTeacher = false }) {
    return (
        <>
            <h2 id="queries">{isTeacher ? "Let's look at your students' queries" : "Let's look at your queries"}</h2>
            <LearningStatsQueries classId={classId} exerciseId={exerciseId} isTeacher={isTeacher} />

            <hr />
            <h2 id="messages">Turning Questions Into Progress</h2>
            <LearningStatsMessages classId={classId} exerciseId={exerciseId} isTeacher={isTeacher} />

            <hr />
            <h2 id="errors">Where things got tricky</h2>
            <LearningStatsErrors classId={classId} exerciseId={exerciseId} isTeacher={isTeacher} />
        </>
    );
}

export default LearningStatsAll;