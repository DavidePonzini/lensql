import { useState } from 'react';

function useToken() {
    const oldToken = JSON.parse(sessionStorage.getItem('token'));

    const [token, setToken] = useState(oldToken);

    const saveToken = userToken => {
        sessionStorage.setItem('token', JSON.stringify(userToken));
        setToken(userToken);
    };

    return [
        token,
        saveToken
    ];
}

export default useToken;