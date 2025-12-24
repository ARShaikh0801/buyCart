document.addEventListener("DOMContentLoaded", function () {

    if (typeof Quill === "undefined") {
        console.error("Quill not loaded");
        return;
    }

  
    if (window.ImageResize && window.ImageResize.default && (!Quill.__imageResizeRegistered)) 
    {
        Quill.register("modules/imageResize", window.ImageResize.default);
        Quill.__imageResizeRegistered = true;
    }
     else {
        console.warn("ImageResize module not found or invalid");
    }

    document.querySelectorAll("textarea.quill-editor").forEach(function (textarea) {

    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";
    textarea.style.height = "0";
    textarea.style.width = "0";

    const toolbar = document.createElement("div");
    toolbar.innerHTML = `
        <span class="ql-formats">
          <select class="ql-font"></select>
          <select class="ql-size"></select>
        </span>
        <span class="ql-formats">
          <button class="ql-bold"></button>
          <button class="ql-italic"></button>
          <button class="ql-underline"></button>
          <button class="ql-strike"></button>
        </span>
        <span class="ql-formats">
          <select class="ql-color"></select>
          <select class="ql-background"></select>
        </span>
        <span class="ql-formats">
          <button class="ql-script" value="sub"></button>
          <button class="ql-script" value="super"></button>
        </span>
        <span class="ql-formats">
          <button class="ql-header" value="1"></button>
          <button class="ql-header" value="2"></button>
          <button class="ql-blockquote"></button>
          <button class="ql-code-block"></button>
        </span>
        <span class="ql-formats">
          <button class="ql-list" value="ordered"></button>
          <button class="ql-list" value="bullet"></button>
          <button class="ql-indent" value="-1"></button>
          <button class="ql-indent" value="+1"></button>
        </span>
        <span class="ql-formats">
          <button class="ql-direction" value="rtl"></button>
          <select class="ql-align"></select>
        </span>
        <span class="ql-formats">
          <button class="ql-link"></button>
          <button class="ql-image"></button>
          <button class="ql-video"></button>
          <button class="ql-formula"></button>
        </span>
        <span class="ql-formats">
          <button class="ql-clean"></button>
        </span>
        `;

    textarea.parentNode.insertBefore(toolbar, textarea);

    const editor = document.createElement("div");
    editor.style.minHeight = "300px";
    textarea.parentNode.insertBefore(editor, textarea.nextSibling);

    const quill = new Quill(editor, {
        theme: "snow",
        modules: {
            syntax: true,
            toolbar: toolbar,
            imageResize: {
                displaySize: true
            }
        },
        placeholder: "Compose an epic..."
    });

    quill.root.innerHTML = textarea.value;

    textarea.closest("form").addEventListener("submit", function () {
        textarea.value = quill.root.innerHTML;
    });
});
});
