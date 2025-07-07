// ********** imports **********
import * as fetches from "./fetches";

// ********** Header search logic **********
let searchInput = document.getElementById("searchInput");
let searchInputDiv = document.getElementById("search");
let inputTimeout = 500;
let usersDivActive = false;
let usersDiv;
let activeTimeout;
// relating to the dropdown list
let currentItem;
searchInput.addEventListener("input",  () => {
    clearTimeout(activeTimeout)
    activeTimeout = setTimeout(async () => {
        let q = searchInput.value;
        if (q !== "") {
            let res = await fetches.fetchUsers(q);
            if (res.error) {
                console.log(res.message);
            } else {
                if (res.length > 0) {
                    if (usersDivActive === false) {
                        // created the list div
                        createDropDownDiv(searchInputDiv);
                        usersDivActive = true;
                    } else {
                        // removing all user suggestions from old search
                        removeDropDownChildren(usersDiv);
                    }

                    for (let i = 0; i < res.length; i++) {
                        let user = res[i];
                        // creating each list item
                        let span = document.createElement("span");
                        span.className = "user-dropdown-item";
                        span.dataset.userPk = user["id"];
                        span.innerText = `${user["firstName"]} ${user["lastName"]}`;
                        addListener("mouseup", span);
                        usersDiv.appendChild(span);
                    }

                    // adding listeners to the users list
                    addListener("keydown", searchInput, Array.from(usersDiv.children));
                    addListener("focusout", searchInput);
                }
            }
        } else {
            usersDivActive = false;
            removeListener("keydown", searchInput);
            removeListener("focusout", searchInput);
        }
    }, inputTimeout);
});

// ***** Header search functions *****
function createDropDownDiv(parent) {
    usersDiv = document.createElement("div");
    usersDiv.id = "usersDiv";
    parent.appendChild(usersDiv);
}

function removeDropDownDiv(parent, elId) {
    let el = document.getElementById(elId);
    if (el) {
        parent.removeChild(el)
        removeListener("keydown", searchInput);
        removeListener("focusout", searchInput);
    }
}

function removeDropDownChildren(parent) {
    while (parent.childElementCount > 0) {
        parent.removeChild(parent.firstElementChild);
    }
}

function selectUser(userPk) {
    window.location.href = `/customers/view/${userPk}/`;
}

const keyDownFunction = (ev, refList = null) => {
    let currentItem = getCurrentItem();
    let itemIndex = !currentItem ? 0 : refList.indexOf(currentItem);
    let nextItem = refList[itemIndex] === refList[refList.length - 1] ? refList[0] : refList[itemIndex + 1];
    let previousItem = refList[itemIndex] === refList[0] ? refList[refList.length - 1] : refList[itemIndex - 1];
    let newCurrentItem;
    switch(ev.key) {
        case "ArrowDown":
            newCurrentItem = !currentItem ? refList[0] : nextItem;
            // adding the active class to the current Item
            newCurrentItem.classList.add("active-item");
            // removing the active class from previous item
            refList.filter(item => {
                if (item.className.includes("active-item") && item !== newCurrentItem) {
                    item.classList.remove("active-item");
                }
            });
            // setting the new currentIndex
            setCurrentItem(newCurrentItem);
            break;
        case "ArrowUp":
            newCurrentItem = previousItem;
            // adding the active class to the current Item
            newCurrentItem.classList.add("active-item");
            // removing the active class from previous item
            refList.filter(item => {
                if (item.className.includes("active-item") && item !== newCurrentItem) {
                    item.classList.remove("active-item");
                }
            });
            // setting the new currentIndex
            setCurrentItem(newCurrentItem);
            break;
        case "Escape":
            removeDropDownDiv(searchInputDiv, usersDiv.id);
            ev.target.value = "";
            ev.target.blur();
            break;
        case "Enter":
            let activeItem = usersDiv.querySelector(".active-item");
            let userPk = activeItem.dataset.userPk;
            selectUser(userPk);
            break;
        default:
            break;
    }
}

function focusOutFunction() {
    setTimeout(() => {
        removeDropDownDiv(searchInputDiv, usersDiv.id);
    }, 250);
    searchInput.value = "";
    removeListener("keydown", searchInput);
    removeListener("focusout", searchInput);
}

function clickFunction(ev) {
    let userPk = ev.target.dataset.userPk;
    selectUser(userPk);
}

function getCurrentItem() {
    return currentItem
}

function setCurrentItem(newItem) {
    currentItem = newItem;
}

// ***** Header search listeners *****
let eventTypes = {
    keydown: keyDownFunction,
    focusout: focusOutFunction,
    mouseup: clickFunction,
}

function addListener(type, el, refList=null) {
    el.addEventListener(type, (ev) => eventTypes[type](ev, refList));
}

function removeListener(type, el) {
    el.removeEventListener(type, eventTypes[type]);
}