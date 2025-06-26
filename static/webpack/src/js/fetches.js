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

export const submitActivityNote = async (form) => {
    let formData = new FormData(form);
    return await fetch('/fetch-submit-form/',  {
        method: 'post',
        headers: {
            'X-CSRFToken': functions.getCookie("csrftoken"),
        },
        body: formData,
    }).then(async response => {
        return response.json()
    })
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

export const fetchModalData = async (modalData) => {
    let url = '/fetch-modal-data/?' + new URLSearchParams(modalData);
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