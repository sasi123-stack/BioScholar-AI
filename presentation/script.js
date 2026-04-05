const slides = document.querySelectorAll('.slide');
const prevBtn = document.getElementById('prevSlide');
const nextBtn = document.getElementById('nextSlide');
const indicator = document.querySelector('.curr-slide-indicator');

let currentSlide = 0;

function updateSlides() {
    slides.forEach((slide, index) => {
        slide.classList.remove('active', 'prev');
        if (index === currentSlide) {
            slide.classList.add('active');
        } else if (index < currentSlide) {
            slide.classList.add('prev');
        }
    });

    // Update Indicator
    const slideNum = (currentSlide + 1).toString().padStart(2, '0');
    const totalSlides = slides.length.toString().padStart(2, '0');
    if (indicator) indicator.innerText = `${slideNum} / ${totalSlides}`;

    // Update Buttons
    if (prevBtn) prevBtn.disabled = currentSlide === 0;
    if (nextBtn) nextBtn.innerText = currentSlide === slides.length - 1 ? 'FINISH' : 'NEXT';

    // Update Projector/Speaker Notes
    const notesElement = slides[currentSlide].querySelector('.speaker-notes');
    const activeNote = document.getElementById('activeNote');
    
    if (notesElement && activeNote) {
        const text = notesElement.innerText.trim();
        console.log(`Setting Note for Slide ${currentSlide + 1}: ${text}`);
        activeNote.innerHTML = text;
    } else {
        console.warn(`Notes not found for Slide ${currentSlide + 1}`);
    }
}

function nextSlide() {
    if (currentSlide < slides.length - 1) {
        currentSlide++;
        updateSlides();
    }
}

function prevSlide() {
    if (currentSlide > 0) {
        currentSlide--;
        updateSlides();
    }
}

function toggleNotes() {
    const notesModal = document.getElementById('notesModal');
    if (!notesModal) return;
    const currentDisplay = window.getComputedStyle(notesModal).display;
    if (currentDisplay === 'none') {
        notesModal.style.display = 'flex';
    } else {
        notesModal.style.display = 'none';
    }
}

// Event Listeners
if (nextBtn) nextBtn.addEventListener('click', nextSlide);
if (prevBtn) prevBtn.addEventListener('click', prevSlide);

document.addEventListener('keydown', (e) => {
    const key = e.code;
    if (key === 'Space' || key === 'ArrowRight') {
        e.preventDefault();
        nextSlide();
    }
    if (key === 'ArrowLeft') {
        e.preventDefault();
        prevSlide();
    }
    if (key === 'KeyN') {
        e.preventDefault();
        toggleNotes();
    }
    if (key === 'Escape') {
        const notesModal = document.getElementById('notesModal');
        if (notesModal) notesModal.style.display = 'none';
    }
});

// Expose to window for the onclick attribute
window.toggleNotes = toggleNotes;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateSlides();
    console.log("BioMedScholar Presentation Script Loaded");
});
