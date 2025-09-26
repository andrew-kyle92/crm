import {dragStart, moveElement} from "../functions";
import * as functions from "../functions";
import {dragged} from "../main";

export function initHouseholdFormLogic() {
    const customers = Array.from(document.getElementsByClassName("customer"));
    let hiddenMembers = Array.from(document.getElementById("id_members").options);
    const membersDiv = document.getElementById("membersDiv");

    customers.forEach(customer => {
        customer.addEventListener("dragstart", dragStart);
    });

    // hiding all members withing the head of household input
    let headOfHouseholdSelect = document.getElementById("id_head_of_household");
    let headOfHouseholdOptions = Array.from(headOfHouseholdSelect.querySelectorAll("option")).filter(el => el.value !== "");
    headOfHouseholdOptions.forEach(option => {
        option.hidden = true;
    });

    // detecting any changes to the membersDiv
    let config = {
        childList: true
    }
    const mutationCallback = function (mutationList, observer) {
        for (const mutation of mutationList) {
            if (mutation.target.childElementCount > 0) {
                mutation.target.classList.remove("add-space");
            } else {
                if (!mutation.target.className.includes("add-space")) {
                    mutation.target.classList.add("add-space");
                }
            }
        }
    }
    const observer = new MutationObserver(mutationCallback);
    observer.observe(membersDiv, config);

    // listener logic
    membersDiv.addEventListener("dragover", (e) => {
        // removing the default behavior
        e.preventDefault();
        membersDiv.classList.add("dragover");
    });

    membersDiv.addEventListener("dragleave", (e) => {
        e.preventDefault();
        membersDiv.classList.remove("dragover");
    });

    membersDiv.addEventListener("drop", (e) => {
        e.preventDefault();

        let addRemoveBtn = dragged.querySelector(".add-remove-button-div button");
        let data = functions.getData(dragged, membersDiv, addRemoveBtn, hiddenMembers, headOfHouseholdOptions, "add")

        moveElement(data);
        membersDiv.classList.remove("dragover");
    });

    // add/remove button logic and dblclick handler for customer div
    let addRemoveBtns = Array.from(document.querySelectorAll(".add-remove-button-div button"));
    addRemoveBtns.forEach(btn => {
        let custNode = btn.parentNode.parentNode;
        let data;
        if (btn.classList.contains("add-customer")) {
            data = functions.getData(custNode, membersDiv, btn, hiddenMembers, headOfHouseholdOptions, "add");
        } else {
            data = functions.getData(custNode, membersDiv, btn, hiddenMembers, headOfHouseholdOptions, "remove");
        }

        let moveHandler = () => moveElement(data);
        btn.addEventListener("click", moveHandler);
        // listener for when you double-click the customer's div
        custNode.addEventListener("dblclick", moveHandler);
    });

    // finding all initial members
    hiddenMembers.forEach(member => {
        if (member.selected) {
            let memberOption = customers.find((el) => el.dataset.customerId === member.value);
            let addRemoveBtn = memberOption.querySelector(".add-remove-button-div button");
            let data = functions.getData(memberOption, membersDiv, addRemoveBtn, hiddenMembers, headOfHouseholdOptions, "add")
            moveElement(data, true);
        }
    });
}