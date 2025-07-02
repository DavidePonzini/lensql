import AppName from '../components/AppName';

import { NavLink } from 'react-router-dom';

function Home() {

    return (
        <div>
            {/* ───── Hero ───── */}
            <header className='py-5 text-center bg-light'>
                <div className='container'>
                    <h1 className='display-4 fw-bold mb-3'>
                        Learn SQL through Exploration with
                        <br />
                        <b><AppName /></b>
                    </h1>
                    <p className='lead mb-4'>
                        Your personal AI companion for mastering query logic, not just syntax.
                    </p>
                    <div>
                        <NavLink to='/register' className='btn btn-primary btn-lg me-2'>Get Started</NavLink>
                        <NavLink to='/about' className='btn btn-outline-secondary btn-lg'>Learn More</NavLink>
                    </div>
                </div>
            </header>

            {/* ───── What is LensQL ───── */}
            <section className='py-5'>
                <div className='container'>
                    <h2 className='h3 mb-3'>What is LensQL?</h2>
                    <p className='fs-5'>
                        LensQL is an interactive AI assistant that helps learners uncover <em>why</em> their SQL
                        queries behave the way they do. Instead of providing answers, LensQL guides students
                        to discover solutions through constructive feedback and minimal examples.
                    </p>
                </div>
            </section>

            {/* ───── Key Features ───── */}
            <section className='py-5 bg-light'>
                <div className='container'>
                    <h2 className='h3 text-center mb-4'>Key Features</h2>
                    <ul className='list-group list-group-flush mx-auto' style={{ maxWidth: 720 }}>
                        <li className='list-group-item'>🧠 <b>Error Explanations</b> – understand not just <em>what</em> is wrong, but <em>why</em>.</li>
                        <li className='list-group-item'>🔍 <b>Query Descriptions</b> – see what your SQL query actually does.</li>
                        <li className='list-group-item'>🧪 <b>Examples &amp; Analogies</b> – grasp tough concepts via minimal, targeted examples.</li>
                        <li className='list-group-item'>🔁 <b>Iterative Debugging</b> – refine your thinking step by step.</li>
                        <li className='list-group-item'>🎯 <b>Competency-Focused</b> – encourages deep understanding over rote copying.</li>
                    </ul>
                </div>
            </section>

            {/* ───── Why It Works ───── */}
            <section className='py-5'>
                <div className='container'>
                    <h2 className='h3 mb-3'>Why LensQL Works for Learning</h2>
                    <p className='fs-5'>
                        Grounded in research on constructive feedback and struggle-based learning,
                        LensQL promotes durable mastery of concepts such as joins, grouping, and subqueries.
                        Unlike autograders that simply mark queries right or wrong, Lens fosters the mental
                        models students need for real-world SQL.
                    </p>
                </div>
            </section>

            {/* ───── Getting Started ───── */}
            <section className='py-5 bg-light text-center'>
                <div className='container'>
                    <h2 className='h3 mb-3'>Ready to Explore SQL?</h2>
                    <p className='fs-5 mx-auto' style={{ maxWidth: 800 }}>
                        Create a free account to begin using <AppName />.
                        Whether you're a student or an enthusiast, LensQL will guide you with insightful feedback at every step.
                    </p>
                    <NavLink to='/register' className='btn btn-primary btn-lg mt-3'>Sign Up Now</NavLink>
                </div>
            </section>
        </div>
    );
}

export default Home;
