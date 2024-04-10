// Cache frequently accessed DOM elements
const elements = {
    spinner: document.getElementById('spinner'),
    fileExplorer: document.getElementById('file-explorer'),
    log: document.getElementById('log'),
    fileList: document.getElementById('file-list'),
    pattern: document.getElementById('pattern'),
    useIndex: document.getElementById('useIndex'),
    header: document.getElementById('header')
};

function setLoading(isLoading) {
    // elements.spinner.style.display = isLoading ? "block" : "none";
    // elements.fileExplorer.style.display = !isLoading ? "block" : "none";
    // elements.spinner.classList.toggle('hidden');
    // elements.fileExplorer.classList.toggle('hidden');

    if (isLoading && isLoading) {
        elements.spinner.classList.remove('hidden');
        elements.fileExplorer.classList.add('hidden');
    } else {
        elements.spinner.classList.add('hidden');
        elements.fileExplorer.classList.remove('hidden');
    }
}

eel.load_index_into_memory();

eel.expose(printToConsole);
function printToConsole(message) {
    elements.log.innerHTML = `<div>${message}</div>`;
}

function createCell(row, content, dataLabel, isIcon = false) {
    let cell = row.insertCell();
    if (isIcon) {
        let span = document.createElement('span');
        span.classList.add('text-overflow', dataLabel);
        span.textContent = content;
        cell.appendChild(span);
    } else {
        cell.textContent = content;
    }
    cell.setAttribute('data-label', dataLabel);
}

function addFileToExplorer(file, addIcon = true) {
    const row = elements.fileList.insertRow();
    row.addEventListener('dblclick', () => eel.open_file_or_directory(file.path));

    createCell(row, addIcon ? (file.type === "file" ? "📄 " + file.name : "📁 " + file.name) : file.name, 'Name', true);
    createCell(row, file.path, 'Path', true);
    createCell(row, formatSize(file.size), 'Size');
    createCell(row, file.type, 'Type');
    
    let lastModified = new Date(file.last_modified * 1000);
    createCell(row, isNaN(lastModified.getTime()) ? "Invalid Date" : lastModified.toLocaleString(), 'Last Modified');
}

function formatSize(size) {
    if (isNaN(size) || size < 0) {
        return "Invalid size";
    }
    
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let count = 0;

    while (size >= 1024 && count < units.length - 1) {
        size /= 1024;
        count++;
    }

    return `${size.toFixed(2).replace(/\.00$/, '').replace(/(\.\d)0$/, '$1')} ${units[count]}`;
}

eel.expose(updateIndex);
function updateIndex() {
    setLoading(true);
    eel.update_index(() => setLoading(false));
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

const processFilesDebounced = debounce(async () => {
    let pattern = elements.pattern.value;
    let useIndex = elements.useIndex.checked;
    if (!pattern) {
        setLoading(false);
        return;
    }
    setLoading(true);
    let files = await eel.search_files(pattern, useIndex)();
    setLoading(false);
    elements.fileList.innerHTML = '';
    if (files.length > 0) {
        printToConsole(`Found ${files.length} files matching '${pattern}':`);
        files.forEach(file => addFileToExplorer(file, true));
    }
}, 500);

document.addEventListener('DOMContentLoaded', () => {
    elements.pattern.addEventListener('input', processFilesDebounced);
});

function sortTable(columnIndex) {
    setLoading(true);
    let table = document.getElementById('file-list');
    let rows = Array.from(table.rows);
    let dir = table.getAttribute('data-sort-dir') === 'asc' ? 'desc' : 'asc';
    table.setAttribute('data-sort-dir', dir);

    let lastModifiedValue = row.cells[4].getAttribute('data-last-modified');
    let sortedFiles = rows.map(row => ({
        name: row.cells[0].getElementsByClassName('file-name')[0].textContent.replace(/📄 |📁 /g, ""),
        path: row.cells[1].getElementsByClassName('file-path')[0].textContent,
        size: row.cells[2].textContent,
        type: row.cells[3].textContent,
        last_modified: lastModifiedValue || row.cells[4].textContent.trim()
    })).sort((a, b) => {
        let valA = (columnIndex === 4) ? new Date(a.last_modified).getTime() : a[columnIndex].toLowerCase();
        let valB = (columnIndex === 4) ? new Date(b.last_modified).getTime() : b[columnIndex].toLowerCase();
        if (!isNaN(valA) && !isNaN(valB)) {
            return (valA - valB) * (dir === 'asc' ? 1 : -1);
        }
        return valA.localeCompare(valB) * (dir === 'asc' ? 1 : -1);
    });

    rebuildTable(sortedFiles, true);
    setLoading(false);
}

function rebuildTable(files, addIcon) {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';
    files.forEach(file => addFileToExplorer(file, addIcon));
}
