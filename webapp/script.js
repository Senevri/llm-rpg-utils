const base_url = "/api/v1"

function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto'; // Reset height to recalculate
    if (textarea.scrollHeight < 800) {
        textarea.style.height = textarea.scrollHeight + 'px';
    } else {
        textarea.style.height = '700px';
    }
}

function check_collapse(textarea) {
    if (!textarea) {
        return
    }
    if (textarea.classList.contains('show-textarea')) {
        adjustTextareaHeight(textarea);
    }
    else {
        textarea.style.height = "0px"
    }

}

function toggleTextareas(event, id) {

    console.log("event:" + event)
    console.log("id:" + id)
    _target = event.target.getAttribute('for')
    console.log("for:" + _target)
    if (_target === 'all') {
        // Show all textareas
        document.querySelectorAll('.textarea-container textarea').forEach(textarea => {
            console.log("area " + id)
            textarea.classList.toggle('show-textarea');
            textarea.classList.toggle('hide-textarea');
            check_collapse(textarea)
        });
    } else {
        _id = _target
        // Toggle individual textarea
        console.log("test: " + _id)
        const querystr = `#${_id}`
        console.log("query: " + querystr)
        const textarea = document.querySelector(querystr); // Directly select the textarea within the container
        // const textarea_div = event.target
        console.log(["textarea:", textarea])
        if (textarea) { // Check if textarea is found (important in case of typos or dynamic changes)
            textarea.classList.toggle('show-textarea'); // Use toggle to add/remove class
            textarea.classList.toggle('hide-textarea');
            check_collapse(textarea)
        }
        const querystr_cnt = ".textarea-container #div_" + _id
        console.log("query: " + querystr_cnt)
        const textarea_div = document.querySelector(querystr_cnt)
        console.log(["textarea_div:", textarea_div])

        check_collapse(textarea_div);
    }
}
function updateTextarea(text, id) {
    console.log("updateTextarea")
    console.log([text, id])
    const textarea1 = document.getElementById(id);
    if (textarea1) {
        textarea1.value = text;
        textarea1.dispatchEvent(new Event('input'));
    }
}

function fetchTextareaContent(textarea) {
    const url = base_url + '/get_textarea_content/' + textarea.id
    console.log()
    fetch(url)
        .then(response => response.text())
        .then(text => {
            console.log(text)
            updateTextarea(text, textarea.id);
        })
        .catch(error => console.error('Error fetching ' + textarea.id + ' content:', error));
}

function updateConfig(text, area) {
    const data = {
        content: text,
        area: area,
    }
    updateStatus("updating config" + area + "...")
    fetch(base_url + '/update_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },

        body: JSON.stringify(data),
    })
        .then(response => {
            if (!response.ok) {
                updateStatus(response.statusText)
                throw new Error('Network response was not ok');

            }
            updateStatus("ok")
            document.querySelectorAll('textarea').forEach(textarea => {
                if (textarea.id != area) {
                    fetchTextareaContent(textarea)
                    check_collapse(textarea)
                }
            })
        })
        .catch(error => console.error('Error updating ' + area + ' content:', error));
}

function try_update_textareas(config_text) {
    updateConfig(config_text, "textarea_config")
    // const lines = config_text.split('\n');

    // lines.forEach(line => {
    //     if (line[0] == "#") {
    //         return
    //     }
    //     const parts = line.split('=');
    //     if (parts.length === 3) {
    //         const id = parts[1].trim();
    //         const textarea = document.querySelector(`#${id}`);
    //         if (textarea) {
    //             console.log(textarea)
    //             //label.setAttribute('', )
    //         }
    //     }
    // });
}

function sendTextareaContent(text, area) {
    console.log("sendTextareaContent")
    console.log([text, area])
    const data = {
        content: text,
        area: area,
    }
    updateStatus("saving " + area + "...")
    fetch(base_url + '/update_textarea_content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },

        body: JSON.stringify(data),
    })
        .then(response => {
            if (!response.ok) {
                updateStatus(response.statusText)
                throw new Error('Network response was not ok');

            }
            updateStatus("saved " + area + " successfully")
        })
        .catch(error => console.error('Error updating ' + area + ' content:', error));
}

function updateStatus(new_status) {
    elem = document.getElementById("laststatus")
    elem.textContent = new_status
}


function loadlabels(event, params) {
    console.log("loadlabels")
    const config_textarea = document.getElementById("textarea_config")
    if (config_textarea) {
        const config_text = config_textarea.value
        const lines = config_text.split('\n');
        lines.forEach(line => {
            if (line[0] == "#") {
                return
            }
            const parts = line.split('=');
            if (parts.length === 2) {
                const id = parts[0].trim();
                const labelText = parts[1].trim();
                const label = document.querySelector(`label[for="${id}"]`);
                if (label) {
                    label.textContent = labelText;
                    //label.setAttribute('', )
                }
            }
        });
    }
}


document.addEventListener('DOMContentLoaded', function () {
    const elem_functions = [
        {
            selector: "#btn_toggle_all",
            event: "click",
            evnt_fn: toggleTextareas,
            params: "all"


        },
        {
            multi: true,
            selector: "button.toggle-btn",
            event: "click",
            evnt_fn: (event, params) => {
                console.log("params: " + params)
                const target = event.target
                const id = target.getAttribute('for')
                toggleTextareas(event, id)
            }

        },
        {
            multi: true,
            selector: "button.save-btn",
            event: "click",
            evnt_fn: (event, params) => {
                console.log("params: " + params)
                const target = event.target
                const id = target.getAttribute('for')
                content = document.getElementById(id).value
                sendTextareaContent(content, id)
            }

        },
        {
            multi: true,
            selector: "label",
            event: "click",
            evnt_fn: (event, params) => {
                const target = event.target
                const id = target.getAttribute('for')
                toggleTextareas(event, id)
            }
        },
        {
            multi: true,
            selector: "textarea",
            event: "input",
            evnt_fn: (event, params) => {
                const target = event.target
                const id = target.id
                const value = target.value
                // sendTextareaContent(target.value, target.id)
            }
        },
        {
            selector: "#textarea_config",
            event: "input",
            evnt_fn: (event, params) => {
                console.log("loadlabels lambda")
                loadlabels(event, params)
                try_update_textareas(event.target.value)
            },
            params: "all"


        },
    ]

    for (const o of elem_functions) {
        var elems
        console.log(o)
        if (o.multi) {
            elems = document.querySelectorAll(o.selector)
        }
        else {
            const elem = document.querySelector(o.selector)
            elems = [elem]
            console.log(["sempai", elem])
        }
        for (const elem of elems) {
            if (elem) {
                elem.addEventListener(o.event, (event) => o.evnt_fn(event, o.params))
            }
            else {
                console.error(`Element with selector ${o.selector} not found.`);
            }
        }
    }
    // document.querySelectorAll('label').forEach(label => {
    //     label.addEventListener('click', function () {
    //         target = label.getAttribute('for')
    //         toggleTextareas(target)
    //     })
    // })

    const textareas = document.querySelectorAll("textarea")
    textareas.forEach(textarea => {
        fetchTextareaContent(textarea)
        textarea.addEventListener('input', function () {
            adjustTextareaHeight(this);
        });
        // Adjust height on initial load as well if there's default content
        adjustTextareaHeight(textarea);
    });
});
