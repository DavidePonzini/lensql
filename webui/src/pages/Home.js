import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import Parallax from '../components/Parallax';
import AlertUnderDevelopment from '../components/AlertUnderDevelopment';

import bg from '../res/database.jpg';

function Home() {
    const { isLoggedIn } = useAuth();

    return (
        <Parallax image={bg}>
            <div className="container pt-5 px-0 bg-light">

                {/* 1. Hero Section */}
                <section className="text-center p-3">
                    <h1 className="display-4 fw-bold text-primary">
                        Learn SQL Through Mistakes – With LensQL
                    </h1>
                    <p className="lead text-secondary">
                        Discover SQL. Learn from your errors. Grow with Lens.
                    </p>
                    <p className="fs-5">
                        LensQL is an AI-powered SQL learning platform that turns student mistakes into personalized, interactive learning moments.
                    </p>
                    <div className="mt-4">
                        <Link to={isLoggedIn ? "/classes" : "/register"} className="btn btn-primary me-3">
                            Create or Join a Course
                        </Link>
                        <Link to="/about" className="btn btn-outline-success">
                            How LensQL Works
                        </Link>
                    </div>
                </section>

                {/* 2. What is LensQL */}
                <section className="text-center p-3 bg-white">
                    <h2 className="text-success mb-3">What is LensQL?</h2>
                    <p className="fs-4">
                        A smarter way to learn SQL — grounded in your mistakes, powered by AI.
                    </p>
                    <div className="row justify-content-center mt-4">
                        <div className="col-md-8 text-start">
                            <ul className="list-unstyled fs-5">
                                <li>🤖 <strong>AI-driven tutor</strong> that helps students debug queries and think critically</li>
                                <li>🧠 <strong>Error-based pedagogy</strong>: Learn from syntax, logic, and semantic mistakes</li>
                                <li>🎯 <strong>Personalized assignments and dashboards</strong> based on real progress</li>
                            </ul>
                        </div>
                        <blockquote className="blockquote mt-4 fst-italic text-muted">
                            “Over 95% of queries are submitted outside class hours. LensQL supports self-paced, reflective learning.”
                        </blockquote>
                    </div>
                </section>

                {/* 3. How LensQL Works */}
                <section id="how-it-works" className="p-3">
                    <h2 className="text-success text-center mb-4">How LensQL Works</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <ol className="list-group list-group-numbered fs-5">
                                <li className="list-group-item">🧑‍🏫 Teachers create exercises, optionally targeting known error types</li>
                                <li className="list-group-item">🎓 Students solve queries with Lens’ help — no direct answers, only interactive guidance</li>
                                <li className="list-group-item">📊 The system analyzes every query to extract error patterns and track progress</li>
                                <li className="list-group-item">🛠️ Personalized exercises are automatically generated to address specific weaknesses</li>
                                <li className="list-group-item">📈 Learning dashboards show students and teachers how understanding evolves over time</li>
                            </ol>
                            <div className="text-center mt-4">
                                <Link to="/about" className="btn btn-outline-secondary">
                                    See the research behind it
                                </Link>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 4. Meet Lens: Your SQL Sidekick */}
                <section className="p-3 bg-white">
                    <h2 className="text-success text-center mb-4">Meet Lens: Your SQL Sidekick</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <p className="fs-5">
                                Lens used to be an explorer of ancient data relics — until a mysterious SQL query turned them into an AI.
                                Now, Lens guides students through the twists and joins of query logic with curiosity, kindness, and clear feedback.
                            </p>
                            <div className="mt-4">
                                <ul className="list-unstyled fs-5">
                                    <li>❓ <strong>Explains errors</strong> in plain language</li>
                                    <li>📌 <strong>Helps locate mistakes</strong> in your query</li>
                                    <li>🧪 <strong>Shows examples</strong> of similar queries</li>
                                    <li>🧭 <strong>Describes your query's behavior</strong> to help reflect on intent vs result</li>
                                    <li>⚠️ <strong>Gives suggestions only after reflection</strong> — to foster genuine learning</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 5. Why Learn From Errors? */}
                <section className="p-3">
                    <h2 className="text-success text-center mb-4">Why Learn From Errors?</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <div className="row">
                                {/* Students */}
                                <div className="col-md-6 mb-4">
                                    <h5 className="text-primary">For Students</h5>
                                    <ul className="list-unstyled fs-5">
                                        <li>🧠 <strong>Understand the why</strong>, not just the how</li>
                                        <li>🔁 <strong>Improve through iteration</strong> and trial</li>
                                        <li>🚀 <strong>Build debugging and metacognitive skills</strong></li>
                                    </ul>
                                </div>
                                {/* Teachers */}
                                <div className="col-md-6 mb-4">
                                    <h5 className="text-primary">For Teachers</h5>
                                    <ul className="list-unstyled fs-5">
                                        <li>📊 <strong>Identify misconceptions early</strong></li>
                                        <li>🧩 <strong>See learning trajectories</strong>, not just correctness</li>
                                        <li>🛠️ <strong>Tailor support</strong> with data-driven insights</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 6. Gamified Learning That Rewards Effort and Insight */}
                <section className="p-3 bg-white">
                    <h2 className="text-success text-center mb-4">🎮 Gamified Learning That Rewards Effort and Insight</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <p className="fs-5">
                                Learning SQL should feel rewarding — and a little fun, too. LensQL uses two progression systems that motivate students to practice, reflect, and grow.
                            </p>

                            <h4 className="mt-4 text-primary">🔹 XP and Levels — Progress Through Practice</h4>
                            <p className="fs-5">
                                Earn experience by writing and running queries. Leveling up shows your growth over time and rewards consistent effort — not just correct answers.
                            </p>
                            <blockquote className="blockquote text-muted fst-italic">
                                “You don’t need to be perfect — just consistent. The more you experiment, the more you grow.”
                            </blockquote>

                            <h4 className="mt-4 text-primary">🪙 LensCoins — Use Wisely, Reflect Deeply</h4>
                            <p className="fs-5">
                                LensCoins are earned through engagement and spent when asking Lens for help. They encourage students to try before asking — and to reflect on feedback.
                            </p>
                            <blockquote className="blockquote text-muted fst-italic">
                                “LensCoins encourage reflection. Spend them when you're truly stuck — and earn them back by solving more and helping Lens improve.”
                            </blockquote>

                            <h5 className="mt-4 text-success">💡 Why It Works</h5>
                            <ul className="list-unstyled fs-5">
                                <li>🎯 Encourages <strong>experimentation</strong>, not perfection</li>
                                <li>📈 Rewards <strong>consistent effort</strong> and active learning</li>
                                <li>🤝 Builds a <strong>dialogue</strong> between students and the AI assistant</li>
                                <li>🔄 Helps teachers see <strong>who’s trying, not just who’s succeeding</strong></li>
                            </ul>
                        </div>
                    </div>
                </section>


                {/* 7. Your Learning Dashboard */}
                <section className="p-3">
                    <h2 className="text-success text-center mb-4">📊 Your Learning Dashboard</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-10">
                            <div className="row">
                                {/* Students' View */}
                                <div className="col-md-6 mb-4">
                                    <h5 className="text-primary">For Students</h5>
                                    <ul className="list-unstyled fs-5">
                                        <li>🧯 Heatmap of error types</li>
                                        <li>⏱️ Time on task</li>
                                        <li>📘 Concept mastery by topic</li>
                                        <li>📐 Confidence vs correctness chart</li>
                                    </ul>
                                </div>

                                {/* Teachers' View */}
                                <div className="col-md-6 mb-4">
                                    <h5 className="text-primary">For Teachers</h5>
                                    <ul className="list-unstyled fs-5">
                                        <li>📊 Course-wide misconceptions</li>
                                        <li>📈 Exercise effectiveness metrics</li>
                                        <li>🧑‍🏫 Student clustering by learning behavior</li>
                                        <li>🔍 Drill-down into individual learning trajectories</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 8. Try LensQL Now */}
                <section className="p-3 bg-white">
                    <h2 className="text-success text-center mb-4">🚀 Try LensQL Now</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-8 text-center">
                            <p className="fs-5">
                                While LensQL requires registration, here’s a sneak peek of how it helps you reason about errors step by step.
                            </p>

                            {/* Replace src with actual GIF path or embedded player */}
                            <AlertUnderDevelopment />
                            <div className="border rounded shadow-sm p-3 bg-white">
                                <img
                                    src="/demo/lensql-demo.gif"
                                    alt="LensQL query feedback demo"
                                    className="img-fluid rounded"
                                />
                                <small className="d-block text-muted mt-2">
                                    Example: <code>SELECT name FROM students WHERE grade &gt; AVG(grade)</code>
                                </small>
                                <small className="text-muted fst-italic">
                                    Lens identifies a syntax error and explains it in plain language, without giving the answer.
                                </small>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 9. Join the LensQL Community */}
                <section className="p-3">
                    <h2 className="text-success text-center mb-4">🤝 Join the LensQL Community</h2>
                    <div className="row justify-content-center">
                        <div className="col-md-8">
                            <p className="fs-5 text-center mb-4">
                                Already helping <strong>100+ students</strong> outside the classroom.
                            </p>
                            <div className="row">
                                {/* For Teachers */}
                                <div className="col-md-6 mb-4">
                                    <h5 className="text-primary">✅ For Teachers</h5>
                                    <ul className="list-unstyled fs-5">
                                        <li>📚 Create courses</li>
                                        <li>📝 Assign exercises</li>
                                        <li>📊 Track class-wide learning</li>
                                    </ul>
                                </div>

                                {/* For Students */}
                                <div className="col-md-6 mb-4">
                                    <h5 className="text-primary">✅ For Students</h5>
                                    <ul className="list-unstyled fs-5">
                                        <li>💬 Get instant feedback</li>
                                        <li>💡 Practice SQL with purpose</li>
                                        <li>🛠️ Master your weaknesses</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* 10. Call to Action (Again) */}
                <section className="text-center p-3 pb-5 bg-white border-top">
                    <h2 className="mb-3">💡 Learning SQL doesn't start with answers. It starts with errors.</h2>
                    <div className="d-flex justify-content-center gap-3 mt-4">
                        <Link to="/register" className="btn btn-lg btn-primary">
                            Create Your Account
                        </Link>
                        <Link to="/about" className="btn btn-lg btn-outline-success">
                            Learn More
                        </Link>
                    </div>
                </section>

            </div>
        </Parallax>
    );
}

export default Home;
