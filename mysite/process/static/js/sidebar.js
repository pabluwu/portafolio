let arrow = document.querySelectorAll(".arrow");
let linkBtn = document.querySelectorAll(".link_name_parent");

for (let i = 0; i < linkBtn.length; i++) {
    linkBtn[i].addEventListener("click", (e)=>{
        let linkParent = e.target.parentNode.parentNode.parentElement;
        console.log(linkParent)
        linkParent.classList.toggle("showMenu")
    });
    
}

/* for (let i = 0; i < arrow.length; i++) {
    arrow[i].addEventListener("click", (e)=>{
        let arrowParent = e.target.parentElement.parentElement;
        arrowParent.classList.toggle("showMenu")
    });
    
} */

let sidebar = document.querySelector(".sidebar");
let sidebarBtn = document.querySelector(".bx-menu");


sidebarBtn.addEventListener("click", ()=>{
    sidebar.classList.toggle("close");
});

if ($(window).width() < 960) {
    sidebar.classList.toggle("close");
}
