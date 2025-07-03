// ***** This script takes care of functionality relating to all things activity related *****
// ** imports
import * as functions from '../functions';
import * as fetches from '../fetches';

const url = new URL(document.URL);
let pathName = url.pathname;
if (pathName.includes("activity") || pathName.includes("activities")) {
    window.addEventListener("DOMContentLoaded", () => {
        // ***** mark complete logic *****
        let completeButton = document.getElementById("activityCompleteBtn");
        if (completeButton) {
            let activityId = completeButton.dataset.activityId;
            let customerId = completeButton.dataset.customerId;
            completeButton.addEventListener("click", async () => {
                await functions.markActivityComplete(activityId, customerId);
            });
        }
    });
}