/**
 * lunar_phases.js - Dynamic Lunar Phase Descriptions
 * Purpose: Provides spiritual and energetic descriptions for each moon phase
 * Used by the Lunar Information modal for dynamic content
 */

const LunarPhaseDescriptions = {
    "New Moon": {
        title: "New Beginnings",
        description: "The new moon opens a sacred portal of infinite potential and fresh starts. This is the most powerful time for setting intentions, planting seeds of manifestation, and beginning new projects. The invisible moon represents the fertile void where all possibilities exist.",
        energy: "Intention-setting, new beginnings, manifestation, planning, introspection",
        keywords: ["renewal", "possibility", "intention", "birth", "potential"]
    },
    
    "Waxing Crescent": {
        title: "First Light",
        description: "The first tender sliver of lunar light symbolizes hope, emerging intentions, and the delicate beginning of growth. This phase embodies the Maiden archetype and encourages taking the first brave steps toward your dreams and goals.",
        energy: "Hope, emerging growth, taking action, nurturing dreams, gentle progress",
        keywords: ["hope", "growth", "action", "emergence", "courage"]
    },
    
    "First Quarter": {
        title: "Decision Point",
        description: "The half-illuminated moon represents a crucial decision point where intentions meet worldly challenges. This phase demands courage, commitment, and the strength to overcome obstacles on your path to manifestation.",
        energy: "Decision-making, overcoming challenges, commitment, pushing through resistance",
        keywords: ["decision", "challenge", "commitment", "strength", "perseverance"]
    },
    
    "Waxing Gibbous": {
        title: "Refinement",
        description: "The nearly full moon brings energy of refinement, patience, and final preparation. This phase requires dedication and trust as your intentions approach their culmination. It's time to fine-tune your efforts and maintain faith in the process.",
        energy: "Refinement, patience, dedication, fine-tuning, trust in the process",
        keywords: ["refinement", "patience", "dedication", "preparation", "trust"]
    },
    
    "Full Moon": {
        title: "Peak Power",
        description: "The completely illuminated moon represents the zenith of lunar power and manifestation energy. This sacred time brings heightened emotions, spiritual insights, and the harvest of your intentions. It's perfect for celebration, gratitude, and conscious release.",
        energy: "Peak manifestation, heightened intuition, celebration, gratitude, release",
        keywords: ["culmination", "power", "celebration", "insight", "completion"]
    },
    
    "Waning Gibbous": {
        title: "Gratitude & Sharing",
        description: "The beginning of the moon's decrease symbolizes gratitude, sharing wisdom, and the generous distribution of what you've learned. This phase encourages reflection on achievements and teaching others from your experience.",
        energy: "Gratitude, sharing wisdom, reflection, teaching, generous giving",
        keywords: ["gratitude", "wisdom", "sharing", "reflection", "generosity"]
    },
    
    "Third Quarter": {
        title: "Release & Forgiveness",
        description: "The half-moon in decline represents active release, forgiveness, and clearing away what no longer serves. This phase demands conscious letting go and preparation for renewal. It's time for emotional healing and spiritual cleansing.",
        energy: "Release, forgiveness, clearing, letting go, emotional healing",
        keywords: ["release", "forgiveness", "healing", "clearing", "transformation"]
    },
    
    "Waning Crescent": {
        title: "Surrender & Rest",
        description: "The final sliver before darkness symbolizes surrender, deep rest, and integration of wisdom. This is the Crone's sacred time of introspection, spiritual connection, and preparation for the next cycle of growth.",
        energy: "Surrender, rest, introspection, spiritual connection, integration",
        keywords: ["surrender", "rest", "wisdom", "introspection", "preparation"]
    }
};

// Alternative phase names mapping for flexibility
const PhaseNameMapping = {
    "Last Quarter": "Third Quarter",
    "Waning Quarter": "Third Quarter",
    "Disseminating": "Waning Gibbous",
    "Balsamic": "Waning Crescent"
};

/**
 * Get phase description for a given lunar phase
 * @param {string} phaseName - The name of the lunar phase
 * @returns {object} - Phase description object with title, description, energy, and keywords
 */
function getPhaseDescription(phaseName) {
    if (!phaseName) {
        return {
            title: "Lunar Mystery",
            description: "The moon holds ancient wisdom and cosmic secrets, guiding us through cycles of growth, reflection, and transformation.",
            energy: "Cosmic connection, mystery, spiritual guidance",
            keywords: ["mystery", "wisdom", "guidance", "transformation", "cycles"]
        };
    }
    
    // Normalize phase name
    const normalizedName = PhaseNameMapping[phaseName] || phaseName;
    
    return LunarPhaseDescriptions[normalizedName] || LunarPhaseDescriptions["New Moon"];
}

// Export for use in other components
window.LunarPhaseDescriptions = LunarPhaseDescriptions;
window.getPhaseDescription = getPhaseDescription; 