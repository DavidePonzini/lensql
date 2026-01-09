import demo00 from '../res/demo/demo_00.png';
import demo01 from '../res/demo/demo_01.png';
import demo03 from '../res/demo/demo_03.png';
import demo04 from '../res/demo/demo_04.png';
import demo05 from '../res/demo/demo_05.png';
import demo07 from '../res/demo/demo_07.png';
import demo08 from '../res/demo/demo_08.png';
import demo09 from '../res/demo/demo_09.png';
import demo10 from '../res/demo/demo_10.png';
import demo11 from '../res/demo/demo_11.png';
import demo12 from '../res/demo/demo_12.png';
import demo13 from '../res/demo/demo_13.png';
import demo15 from '../res/demo/demo_15.png';
import demo16 from '../res/demo/demo_16.png';
import demo17 from '../res/demo/demo_17.png';
import demo18 from '../res/demo/demo_18.png';
import demo19 from '../res/demo/demo_19.png';
import demo20 from '../res/demo/demo_20.png';
import demo21 from '../res/demo/demo_21.png';
import demo23 from '../res/demo/demo_23.png';

function Tutorial() {
    const demoCarouselImages = [
        demo00, demo01, demo03, demo04, demo05, demo07, demo08, demo09,
        demo10, demo11, demo12, demo13, demo15, demo16, demo17, demo18, demo19,
        demo20, demo21, demo23
    ];

    return (
        <div id="carouselExample" className="carousel carousel-dark slide border" data-bs-ride="carousel">
            <div className="carousel-indicators">
                {
                    demoCarouselImages.map((_, i) => (
                        <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to={i} className={i === 0 ? 'active' : ''} aria-current={i === 0 ? 'true' : undefined} aria-label={`Slide ${i + 1}`} key={`indicator_${i}`}></button>
                    ))
                }
            </div>
            <div className="carousel-inner">
                {demoCarouselImages.map((img, i) => (
                    <div className={`carousel-item${i === 0 ? ' active' : ''}`} key={`demo_img_${i}`}>
                        <img src={img} className="d-block w-100" alt='How LensQL works' />
                    </div>
                ))}
            </div>
            <button className="carousel-control-prev" type="button" data-bs-target="#carouselExample" data-bs-slide="prev">
                <span className="carousel-control-prev-icon" aria-hidden="true"></span>
                <span className="visually-hidden">Previous</span>
            </button>
            <button className="carousel-control-next" type="button" data-bs-target="#carouselExample" data-bs-slide="next">
                <span className="carousel-control-next-icon" aria-hidden="true"></span>
                <span className="visually-hidden">Next</span>
            </button>
        </div>
    );
}

export default Tutorial;