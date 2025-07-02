function CardList({ children }) {
    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
        }}>
            {children}
        </div>
    );
}

export default CardList;