// script.js

// This object holds the relationships between locations and greenhouses
const greenhouseData = {
    TGW: ['2+3', '4', '5', '6', '7'],
    ELN: ['19', '20', '21', '22', '23', '31', '32', '33', '34']
};

// script.js

// This object holds the relationships between Kultur and Sorte
const kulturData = {
    dattelcherry: [
        'SG Adorelle',
        'Prodelle',
        'SG Sweetelle',
        'RZ Parisetto Sanaterra',
        'EZ Icaria',
        'SG Sweetelle Sanaterra',
        'RZ Parisetto'
    ],
    rispentomaten: [
        'Dunk',
        'Climundo',
        'RZ Parisetto',
        'Dunk Sanaterra',
        'Cibello',
        'RZ Parisetto Sanaterra',
        'Dunk T2',
        'RZ 72-IM6752 (22K952609)',
        'Bronski',
        'EZ 3250'
    ],
    gurken: [
        'Georgia',
        'Verdon',
        'Sakata Mackay F1',
        'RZ Blueheaven',
        'RZ Blueheaven 2.5 Pfl/m2',
        'Blueray'
    ],
    aubergine: [] // Aubergine has no specific 'Sorte' options, so we use an empty array
};

// This will store the user's choices as they go through the steps
let selectionState = {
    location: null,
    haus: null
};

// Wait for the entire HTML page to be loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get all the step containers and buttons
    const locationStep = document.querySelector('#location-step');
    const hausStep = document.querySelector('#haus-step');
    const entryStep = document.querySelector('#entry-step');

    const locationButtons = document.querySelectorAll('.location-btn');
    const hausSelect = document.querySelector('#haus-select');
    const kulturSelect = document.querySelector('#kultur-select');
    const sorteSelect = document.querySelector('#sorte-select');

    const goToEntryBtn = document.querySelector('#go-to-entry');
    const backToLocationBtn = document.querySelector('#back-to-location');
    const backToHausBtn = document.querySelector('#back-to-haus');

    // --- Navigation Logic ---

    // Function to show a specific step and hide the others
    const showStep = (stepToShow) => {
        locationStep.classList.add('hidden');
        hausStep.classList.add('hidden');
        entryStep.classList.add('hidden');
        stepToShow.classList.remove('hidden');
    };

    // When a location button is clicked...
    locationButtons.forEach(button => {
        button.addEventListener('click', () => {
            selectionState.location = button.dataset.location;
            populateHausDropdown(selectionState.location);
            showStep(hausStep);
        });
    });

    // When the "Next" button on the Haus step is clicked...
    goToEntryBtn.addEventListener('click', () => {
        selectionState.haus = hausSelect.value;
        if (selectionState.haus) {
            showStep(entryStep);
        } else {
            alert('Please select a greenhouse.');
        }
    });

    // Handle the "Back" buttons
    backToLocationBtn.addEventListener('click', () => showStep(locationStep));
    backToHausBtn.addEventListener('click', () => showStep(hausStep));

    // --- Dynamic Dropdown Logic ---

    // Function to fill the greenhouse dropdown based on location
    const populateHausDropdown = (location) => {
        const houses = greenhouseData[location];
        hausSelect.innerHTML = '<option value="">--Choose Greenhouse--</option>'; // Clear old options
        houses.forEach(haus => {
            const option = document.createElement('option');
            option.value = haus;
            option.textContent = `Haus ${haus}`;
            hausSelect.appendChild(option);
        });
    };
    
    // When the Kultur dropdown changes...
    kulturSelect.addEventListener('change', () => {
        const selectedKultur = kulturSelect.value;
        populateSorteDropdown(selectedKultur);
    });

    // Function to fill the Sorte dropdown based on Kultur
    const populateSorteDropdown = (kultur) => {
        const sorten = kulturData[kultur] || [];
        sorteSelect.innerHTML = '<option value="">--Choose Sorte--</option>'; // Clear old options
        sorten.forEach(sorte => {
            const option = document.createElement('option');
            option.value = sorte;
            option.textContent = sorte;
            sorteSelect.appendChild(option);
        });
    };

    // --- Final Form Submission ---
    const dataEntryForm = document.querySelector('#data-entry-form');
    dataEntryForm.addEventListener('submit', (event) => {
        event.preventDefault();
        // This is where the Phase 3 (Supabase) code will go.
        // For now, we'll just log all the collected data to the console.
        
        const formData = new FormData(dataEntryForm);
        const finalData = {
            location: selectionState.location,
            haus: selectionState.haus,
            kultur: formData.get('kultur'),
            sorte: formData.get('sorte'),
            plant_id: formData.get('plant-id'),
            leaf_count: formData.get('leaf-count'),
            // Add other form fields here...
        };

        console.log('Final data to be sent to Supabase:', finalData);
        alert('Form is ready to be sent! Check the developer console (F12) to see the data.');
    });
});