function download_handler(modelId, model_type) {
    let js_model_txtbox = gradioApp().querySelector('#gr_js_download_model_url textarea');
    let js_download_btn = gradioApp().querySelector('#gr_download_btn');
    if (!js_model_txtbox) return;
    js_model_txtbox.value = modelId+','+model_type;
    js_model_txtbox.dispatchEvent(new Event("input"));
    js_download_btn.click();
}
onUiTabChange(function(){
    let modelDiv = gradioApp().querySelector('#tab_gr_extension_tab')
    if(!modelDiv) return;
    if(modelDiv.style.display == 'block'){
        let searchBtn = gradioApp().querySelector('#gr_search_btn')
        if(!searchBtn) return;
        // searchBtn.click();
        let gr_js_page_number = gradioApp().querySelector('#gr_js_page_number textarea');
        if (!gr_js_page_number) return;
        updatePagination('', searchBtn, gr_js_page_number)
        delegate(document, 'click', '.gr-next-page', function(e){
            let nextPageUrl = this.getAttribute('data-url');
            updatePagination(nextPageUrl, searchBtn, gr_js_page_number)
        });
        // previous page button click
        delegate(document, 'click', '.gr-previous-page', function(e){
            let previousPageUrl = this.getAttribute('data-url');
            updatePagination(previousPageUrl, searchBtn, gr_js_page_number);
        });
    }
});

function updatePagination(nextPrevPageUrl, searchBtn, gr_js_page_number){
    let page = 1;
    if(nextPrevPageUrl) {
        const url = new URL(nextPrevPageUrl);
        const searchParams = url.searchParams;
        page = searchParams.get("page"); // Output: 2
    }
    updatePageNumber(gr_js_page_number, page, searchBtn)
}

function updatePageNumber(gr_js_page_number, page, searchBtn){
    const modelTypes = document.querySelectorAll('input[name=radio-gr_model_types]');
    if(modelTypes){
        modelTypes.forEach(elem => {
           elem.addEventListener('change', function(){
               gr_js_page_number.value = 1;
               gr_js_page_number.dispatchEvent(new Event("input"));
               searchBtn.click();
           });
        });
    }
    const gr_model_name = document.querySelector('#gr_model_name textarea');
    if(gr_model_name){
        gr_model_name.addEventListener('change', function(){
            gr_js_page_number.value = 1;
            gr_js_page_number.dispatchEvent(new Event("input"));
            searchBtn.click();
        });
    }
    const gr_page_limit = document.querySelector('#gr-page-limit input[type=range]');
    if(gr_page_limit){
        gr_page_limit.addEventListener('change', function(){
            gr_js_page_number.value = 1;
            gr_js_page_number.dispatchEvent(new Event("input"));
            searchBtn.click();
        });
    }
    gr_js_page_number.value = page;
    gr_js_page_number.dispatchEvent(new Event("input"));
    searchBtn.click();
}
function delegate(el, evt, sel, handler) {
    el.addEventListener(evt, function(event) {
        var t = event.target;
        while (t && t !== this) {
            if (t.matches(sel)) {
                handler.call(t, event);
            }
            t = t.parentNode;
        }
    });
}