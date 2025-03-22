// script.js

// Select DOM elements
const inputArea = document.getElementById('inputArea');
const outputArea = document.getElementById('outputArea');
const copyButton = document.getElementById('copyButton');

// Initialize Turndown Service
const turndownService = new TurndownService();

// Function to convert input to Markdown
function convertToMarkdown() {
    const inputContent = inputArea.value;
    const markdownContent = turndownService.turndown(inputContent);
    outputArea.value = markdownContent;
}

// Event listener for input changes
inputArea.addEventListener('input', convertToMarkdown);

// Copy Markdown to Clipboard
copyButton.addEventListener('click', () => {
    outputArea.select();
    document.execCommand('copy');
    alert('Markdown copied to clipboard!');
});
