
function Parallax({ image, children }) {
    return (
        <div style={{
            backgroundImage: `url(${image})`,
            backgroundSize: 'cover',
            backgroundAttachment: 'fixed',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
            minHeight: '500px'
        }}>
            {children}
        </div>
    );
}

export default Parallax;
