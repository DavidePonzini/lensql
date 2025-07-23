import { Link } from "react-router-dom";

function About() {
    return (
        <div className="container-md">
            <h1 className="text-center text-primary mb-4">About LensQL</h1>

            <p className="fs-5">
                LensQL is an interactive platform that helps students learn SQL through guided practice, personalized feedback, and gamified progression. Built with both students and teachers in mind, it supports a deeper understanding of relational databases by focusing on the reasoning behind queries — not just their correctness.
            </p>

            <p className="fs-5">
                Instead of offering immediate solutions, LensQL encourages active exploration. The AI assistant, Lens, helps students reflect on their mistakes, refine their logic, and grow their skills with every attempt. Teachers, meanwhile, gain insight into how students learn, where they struggle, and how to support them effectively.
            </p>

            <p className="fs-5">
                Whether you're running your first query or refining complex joins, LensQL turns every error into an opportunity to learn.
            </p>

            <h5 className="mt-5 text-success">🔍 Want to know more?</h5>
            <p className="fs-5 mb-1">
                LensQL is developed as part of ongoing research at the University of Genoa. If you're curious about the academic background or technical details, here are some publications that explore the ideas behind it:
            </p>
            <ul className="fs-6 ps-3">
                <li className="mb-1">
                    <a
                        href="/files/SEBD2025.pdf"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-primary text-decoration-none"
                    >
                        <em>Analyzing Common Student Errors in SQL Query Formulation to Enhance Learning Support</em>
                    </a>{" "}
                    — A large-scale study on student SQL mistakes and how they vary across learning settings.
                </li>
                <li>
                    <a
                        href="/files/ADBIS2025.pdf"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-primary text-decoration-none"
                    >
                        <em>Enhancing SQL Learning through Generative AI and Student Error Analysis</em>
                    </a>{" "}
                    — A framework for AI-assisted feedback, error tracking, and personalized assignment generation in SQL education.
                </li>
            </ul>

            <div className="mt-4 text-center">
                <Link className="btn btn-success" to="/register" role="button">Try LensQL</Link>
            </div>
        </div>
    );
}

export default About;
