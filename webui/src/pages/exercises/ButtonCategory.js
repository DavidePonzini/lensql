function ButtonCategory({ text, className, iconClassName }) {
    return (
        <div
            className={`col-auto ${className}`}
            style={{
                alignContent: 'center',
                marginBottom: '0.25rem',
                width: 120,
            }}
        >
            <i className={`${iconClassName} mx-1`}></i>
            {text}:
        </div>
    );
}

export default ButtonCategory;