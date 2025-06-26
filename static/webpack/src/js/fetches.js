// ***** imports *****
import * as functions from "./functions"

// ***** Fetch requests *****
export const fetchActivity = async (activityId) => {
    let url = '/fetch-activity/?' + new URLSearchParams({activity_id: activityId});
    return await fetch(url, {
        method: 'get',
        credentials: 'same-origin',
        headers: {
            'x-CSRFToken': functions.getCookie("csrftoken"),
        }
    }).then(async response => {
        return response.json()
    });
}

export const fetchUsers = async (q) => {
    let url = '/fetch-users/?' + new URLSearchParams({q: q});
    return await fetch(url, {
        method: 'get',
        credentials: 'same-origin',
        headers: {
            'x-CSRFToken': functions.getCookie("csrftoken"),
        }
    }).then(async response => {
        return response.json()
    });
}