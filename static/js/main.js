// ***** Getting the CSRF Token *****
function getCookie(name) {
    let cookies = document.cookie.split(";");
    cookies.forEach(cookie => {
       let [cookieName, value] = cookie.trim().split("=");
       if (cookieName === name ) {
           return value
       }
    });
}

// ***** Global Script Variables *****
const currentUrl = new URL(document.URL);
const csrfToken = getCookie("csrftoken");

// ***** Fetch requests *****
const fetchActivity = async (activityId) => {
    let url = '/fetch-activity/?' + new URLSearchParams({activity_id: activityId});
    return await fetch(url, {
        method: 'get',
        credentials: 'same-origin',
        headers: {
            'x-CSRFToken': csrfToken,
        }
    }).then(async response => {
        return response.json()
    });
}

// on DOMContentLoaded
window.addEventListener("DOMContentLoaded", () => {
    if (currentUrl.href.includes("activities")) {
        // on click event for activities
        let activities = document.getElementsByClassName("activity");
        for (let i = 0; i < activities.length; i++) {
            let activity = activities[i];
            activity.addEventListener("click", async () => {
               let activityId = activity.dataset.activityId;
               let res = await fetchActivity(activityId);
               if (res.status === "errors") {
                    console.log(res.message);
               } else {
                   let noActivityDiv = document.getElementById("noActivityMsg");
                   let activityDiv = document.getElementById("activityDiv");
                   let activityData = res["activity"];
                   let parser = new DOMParser()
                   let activityHtml = parser.parseFromString(activityData, 'text/html');
                   let activityBody = activityHtml.getElementById(`activityDiv-${activityId}`);

                   // checking to see if any children exist within the activityDiv
                   if (activityDiv.childElementCount > 0) {
                       activityDiv.removeChild(activityDiv.firstElementChild);
                   }
                   activityDiv.appendChild(activityBody);
                   // hiding the no activity div
                   noActivityDiv.hidden = true;
                   // un-hiding the activityDiv
                   activityDiv.hidden = false;
               }
            });
        }
    }

    if (currentUrl.href.includes("customers/add")) {
        // this will only allow digit characters to be entered and formats it on every input character
        let phoneInputs = document.getElementsByClassName("phone");
        for (let i = 0; i < phoneInputs.length; i++) {
            let phoneInput = phoneInputs[i];
            phoneInput.placeholder = "ex (555) 555-5555";
            phoneInput.addEventListener("input", (e) => {
                let x = e.target.value.replace(/\D/g, "").match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
                e.target.value = !x[2] ? x[1] : "(" + x[1] + ") " + x[2] + (x[3] ? "-" + x[3] : "");
            });
        }
    }
});