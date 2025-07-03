// import the custom css
import "../scss/styles.scss";

// imports
import * as bootstrap from "bootstrap";

// ********** Start of main.js script **********
// imports
import * as functions from "./functions";
import * as fetches from "./fetches";
import {applyActivityFilter} from "./functions";

// ***** Global Script Variables *****
const currentUrl = new URL(document.URL);

// on DOMContentLoaded
window.addEventListener("DOMContentLoaded", () => {
    if (currentUrl.href.includes("activities")) {
        // on click event for activities
        let activities = document.getElementsByClassName("activity");
        for (let i = 0; i < activities.length; i++) {
            let activity = activities[i];
            activity.addEventListener("click", async () => {
               let activityId = activity.dataset.activityId;
               let res = await fetches.fetchActivity(activityId);
               if (res.status === "errors") {
                    console.log(res.message);
               } else {
                   let noActivityDiv = document.getElementById("noActivityMsg");
                   let activityDiv = document.getElementById("activityDiv");
                   let activityData = res["activity"];
                   let parser = new DOMParser()
                   let activityHtml = parser.parseFromString(activityData, 'text/html');
                   let activityBody = activityHtml.getElementById(`mainContent`);

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

    // ********** Startup functions ********** //
    let filterBtns = document.getElementsByClassName("applyFilterBtn");
    for (let i = 0; i < filterBtns.length; i++) {
        let filterBtn = filterBtns[i];
        filterBtn.addEventListener("click", () => {
            let valueSourceId = filterBtn.dataset.valueSource;
            let valueSource = document.getElementById(valueSourceId);
            let url = new URL(document.URL);
            let urlData = {}
            if (url.search !== '') {
                let urlParams = new URLSearchParams(url.search);
                urlParams.forEach((value, key) => {
                    urlData[key] = value;
                });
            }
            // adding/updating the filter to match the dropdown selection
            urlData["filter"] = valueSource.value;

            // applying the filters
            applyActivityFilter(urlData);
        });
    }

    // ********** Utility Functions ********** //
    // collapsible sections
    let collapseBtns = document.getElementsByClassName("collapse-btn");
    if (collapseBtns.length > 0) {
        for (let i = 0; i < collapseBtns.length; i++) {
            let collapseBtn = collapseBtns[i];

            collapseBtn.addEventListener("click", () => {
                let target = collapseBtn.dataset.target;
                let collapseType = collapseBtn.dataset.type;
            });
        }
    }

    // get the correct modal content
    let modalDynBtns = document.getElementsByClassName("modal-dyn-btn");
    if (modalDynBtns.length > 0) {
        let contentTypes = {
            note: {
                type: "note",
                title: "Add Note",
                endpoint: new URL(document.URL).pathname + "add-note/",
                activityId: null,
                submitBtnText: "Add Note",
                initEditor: true,
            },
            editNote: {
                type: "editNote",
                title: "Edit Note",
                endpoint: new URL(document.URL).pathname + "add-note/",
                activityId: null,
                submitBtnText: "Save Note",
                initEditor: true,
                instanceId: null,
            }
        }
        for (let i = 0; i < modalDynBtns.length; i++) {
            let modalDynBtn = modalDynBtns[i];
            modalDynBtn.addEventListener("click", async  () => {
                let contentType = modalDynBtn.dataset.contentType;
                let modal = document.getElementById(modalDynBtn.dataset.bsTarget.replace("#", ""));
                let modalInstance = bootstrap.Modal.getOrCreateInstance(modal);
                let modalHeader = modal.querySelector(".modal-title");
                let modalBody = modal.querySelector(".modal-body");
                let modalSubmitBtn = modal.querySelector("#modalSubmitBtn");
                let modalData = contentTypes[contentType];
                modalData.activityId = modalDynBtn.dataset.activityId;
                if (contentType === "editNote") {
                    modalData["instanceId"] = modalDynBtn.dataset.instanceId;
                }
                // getting the html content
                let res = await fetches.fetchModalData(modalData);
                if (res.status === "error") {
                    console.log(res.message);
                } else {
                    // setting up the parser
                    let parser = new DOMParser();
                    // parsing the HTML
                    let html = parser.parseFromString(res.html, "text/html");
                    // getting the form element from the parsed HTML
                    let form = html.querySelector("form");
                    // removing the submit button from the original layout
                    form.removeChild(form.querySelector("#submitBtn"));
                    // changing the modal title and body
                    modalHeader.innerText = modalData.title;
                    modalBody.innerHTML = form.outerHTML;
                    modalSubmitBtn.innerText = modalData.submitBtnText;
                    // updating the modal
                    modalInstance.handleUpdate();

                    if (contentType.initEditor) {
                        // Re-initialize Prose editor
                        if (window.djangoProse && typeof window.djangoProse.init === 'function') {
                            window.djangoProse.init();
                        }
                    }

                    let data;
                    switch (contentType) {
                        case "note":
                            // adding and onclick function
                            data = {
                                notesListId: "notesList",
                                formId: form.id,
                                modalInstance: modalInstance,
                                modal: modal,
                                contentType: contentType,
                            }
                            modalSubmitBtn.addEventListener("click", async () => functions.addActivityNote(data));
                            break;
                        case "editNote":
                            // adding and onclick function
                            data = {
                                notesListId: "notesList",
                                formId: form.id,
                                modalInstance: modalInstance,
                                modal: modal,
                                contentType: contentType,
                                instanceId: modalData["instanceId"],
                            }
                            modalSubmitBtn.addEventListener("click", async () => functions.addActivityNote(data));
                            break;
                    }
                }
            });
        }
    }
});