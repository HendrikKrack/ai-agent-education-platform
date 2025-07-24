import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

interface Persona {
  name: string;
  position: string;
  description: string;
  primaryGoals?: string;
  traits: {
    assertiveness: number;
    cooperativeness: number;
    openness: number;
    risk_tolerance: number;
    emotional_stability: number;
  };
  defaultTraits?: Persona["traits"];
  imageUrl?: string;
}

const traitLabels = [
  { key: "assertiveness", label: "Assertiveness" },
  { key: "cooperativeness", label: "Cooperativeness" },
  { key: "openness", label: "Openness" },
  { key: "risk_tolerance", label: "Risk Tolerance" },
  { key: "emotional_stability", label: "Emotional Stability" },
];

interface PersonaCardProps {
  persona: Persona;
  defaultTraits?: any;
  onTraitsChange?: (traits: any) => void;
  onSave?: (persona: Persona) => void;
  onDelete?: () => void;
  editMode?: boolean;
}

export default function PersonaCard({ 
  persona, 
  defaultTraits, 
  onTraitsChange, 
  onSave, 
  onDelete, 
  editMode = false 
}: PersonaCardProps) {
  const [traits, setTraits] = useState({ ...persona.traits });
  const [editFields, setEditFields] = useState({
    name: persona.name,
    position: persona.position,
    description: persona.description,
    primaryGoals: persona.primaryGoals,
    traits: { ...persona.traits }
  });

  // Sync local traits state with props when persona.traits or defaultTraits change
  useEffect(() => {
    setTraits({ ...persona.traits });
    setEditFields(fields => ({ ...fields, traits: { ...persona.traits } }));
  }, [persona.traits, defaultTraits]);

  // Keep display sliders in sync with parent
  useEffect(() => {
    if (!editMode) setTraits({ ...persona.traits });
  }, [persona.traits, editMode]);

  const handleSliderChange = (key: keyof typeof traits, value: number[]) => {
    if (editMode) {
      setEditFields(fields => ({
        ...fields,
        traits: {
          assertiveness: typeof fields.traits.assertiveness === 'number' ? fields.traits.assertiveness : 1,
          cooperativeness: typeof fields.traits.cooperativeness === 'number' ? fields.traits.cooperativeness : 1,
          openness: typeof fields.traits.openness === 'number' ? fields.traits.openness : 1,
          risk_tolerance: typeof fields.traits.risk_tolerance === 'number' ? fields.traits.risk_tolerance : 1,
          emotional_stability: typeof fields.traits.emotional_stability === 'number' ? fields.traits.emotional_stability : 1,
          [key]: value[0],
        },
      }));
    } else {
      const newTraits = { ...traits, [key]: value[0] };
      setTraits(newTraits);
      if (onTraitsChange) onTraitsChange(newTraits);
    }
  };

  const handleReset = () => {
    if (editMode) {
      setEditFields(fields => ({
        ...fields,
        traits: {
          assertiveness: defaultTraits?.assertiveness ?? 1,
          cooperativeness: defaultTraits?.cooperativeness ?? 1,
          openness: defaultTraits?.openness ?? 1,
          risk_tolerance: defaultTraits?.risk_tolerance ?? 1,
          emotional_stability: defaultTraits?.emotional_stability ?? 1,
        },
      }));
    } else {
      setTraits({
        assertiveness: defaultTraits?.assertiveness ?? 1,
        cooperativeness: defaultTraits?.cooperativeness ?? 1,
        openness: defaultTraits?.openness ?? 1,
        risk_tolerance: defaultTraits?.risk_tolerance ?? 1,
        emotional_stability: defaultTraits?.emotional_stability ?? 1,
      });
      if (onTraitsChange) onTraitsChange({
        assertiveness: defaultTraits?.assertiveness ?? 1,
        cooperativeness: defaultTraits?.cooperativeness ?? 1,
        openness: defaultTraits?.openness ?? 1,
        risk_tolerance: defaultTraits?.risk_tolerance ?? 1,
        emotional_stability: defaultTraits?.emotional_stability ?? 1,
      });
    }
  };

  const handleEditFieldChange = (field: string, value: string) => {
    setEditFields(fields => ({ ...fields, [field]: value }));
  };

  const handleSave = () => {
    if (onSave) {
      onSave({
        ...persona,
        name: editFields.name,
        position: editFields.position,
        description: editFields.description,
        primaryGoals: editFields.primaryGoals,
        traits: { ...editFields.traits },
      });
    }
    // setEditMode(false); // This is now handled by the parent
  };

  const handleDelete = () => {
    if (onDelete) onDelete();
  };

  // Display mode
  if (!editMode) {
    return (
      <Card
        className="flex flex-row items-stretch w-full max-w-4xl min-h-[140px] p-3 mb-3 border border-gray-200 shadow-md cursor-pointer"
        tabIndex={0}
        aria-label={`Edit persona: ${persona.name}`}
      >
        {/* Left: Avatar and Info */}
        <div className="flex flex-col items-center justify-center w-32 mr-4">
          <div className="w-16 h-16 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center mb-1">
            {persona.imageUrl ? (
              <img src={persona.imageUrl} alt={persona.name} className="object-cover w-full h-full" />
            ) : (
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <circle cx="12" cy="8" r="4" />
                <path d="M6 20c0-2.2 3-4 6-4s6 1.8 6 4" />
              </svg>
            )}
          </div>
        </div>
        {/* Middle: Name, Position, Description, Goals */}
        <div className="flex-1 flex flex-col justify-center pr-6">
          <div className="text-xl font-bold leading-tight mb-0.5">{persona.name}</div>
          <div className="text-base text-gray-500 mb-2">{persona.position}</div>
          <div className="text-sm text-gray-800 mb-1">{persona.description}</div>
          {persona.primaryGoals && (
            <div className="text-xs text-blue-800 mt-1">
              <span className="font-semibold">Primary Goals:</span>{" "}
              {(() => {
                // Render as bulleted list if lines start with -, *, or •
                const lines = persona.primaryGoals.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
                const isBulleted = lines.every(l => /^(-|\*|•)\s+/.test(l));
                if (isBulleted) {
                  return (
                    <ul className="list-disc ml-5">
                      {lines.map((l, i) => (
                        <li key={i}>{l.replace(/^(-|\*|•)\s+/, "")}</li>
                      ))}
                    </ul>
                  );
                } else {
                  return persona.primaryGoals;
                }
              })()}
            </div>
          )}
        </div>
        {/* Right: Traits (read-only) */}
        <div className="flex flex-col justify-center min-w-[220px]">
          {traitLabels.map(({ key, label }) => (
            <div key={key} className="flex items-center mb-1.5">
              <span className="w-32 text-right pr-2 text-sm font-medium text-gray-800">{label}</span>
              <div className="flex-1 flex items-center">
                <Slider
                  min={1}
                  max={5}
                  step={1}
                  value={[traits[key as keyof typeof traits] || 1]}
                  disabled
                  className="w-32 mx-1"
                />
                <span className="w-5 text-xs text-gray-500 text-center">{traits[key as keyof typeof traits]}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  // Edit mode (no Card wrapper)
  return (
    <div className="w-full max-w-3xl mx-auto grid grid-cols-2 gap-8 p-8 bg-white rounded-lg shadow-lg">
      {/* Left Column */}
      <div className="flex flex-col space-y-6">
        <div className="flex items-center space-x-4">
          <div className="w-24 h-24 rounded-lg bg-gray-200 overflow-hidden flex items-center justify-center">
            {persona.imageUrl ? (
              <img src={persona.imageUrl} alt={editFields.name} className="object-cover w-full h-full" />
            ) : (
              <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <circle cx="12" cy="8" r="4" />
                <path d="M6 20c0-2.2 3-4 6-4s6 1.8 6 4" />
              </svg>
            )}
          </div>
          <div className="flex-1">
            <span className="block text-gray-700 font-semibold text-lg">Name</span>
            <Input
              id="persona-name"
              className="mt-1 block w-full rounded border-gray-300 text-base font-medium"
              value={editFields.name}
              onChange={e => handleEditFieldChange("name", e.target.value)}
              placeholder="Name"
            />
            <span className="block text-gray-700 font-semibold mt-3">Role/Title</span>
            <Input
              id="persona-role"
              className="mt-1 block w-full rounded border-gray-300 text-base"
              value={editFields.position}
              onChange={e => handleEditFieldChange("position", e.target.value)}
              placeholder="Role/Title"
            />
          </div>
        </div>
        <div>
          <span className="block text-xl font-bold text-gray-800 mb-2">Background/Bio</span>
          <Textarea
            id="persona-bio"
            className="w-full bg-gray-50 resize-none min-h-[180px] text-base border border-gray-200 rounded text-gray-700 focus:ring-2 focus:ring-black focus:border-black"
            value={editFields.description}
            onChange={e => handleEditFieldChange("description", e.target.value)}
            placeholder="Background/Bio"
            rows={11}
          />
        </div>
      </div>
      {/* Right Column */}
      <div className="flex flex-col space-y-6">
        <div>
          <span className="block text-xl font-bold text-gray-800 mb-2">Personality</span>
          <div className="space-y-2">
            {traitLabels.map(({ key, label }) => (
              <div key={key} className="flex items-center">
                <span className="w-40 text-gray-700">{label}</span>
                <Slider
                  min={1}
                  max={5}
                  step={1}
                  value={[editFields.traits[key as keyof typeof traits] || 1]}
                  onValueChange={value => handleSliderChange(key as keyof typeof traits, value)}
                  className="w-36 accent-gray-600 mx-2"
                />
                <span className="ml-2 text-gray-500 text-xs">{editFields.traits[key as keyof typeof traits]}</span>
              </div>
            ))}
          </div>
          <div className="flex justify-end mt-2">
            <Button
              size="sm"
              variant="outline"
              className="w-24"
              onClick={handleReset}
            >
              Reset
            </Button>
          </div>
        </div>
        <div>
          <span className="block text-xl font-bold text-gray-800 mb-2">Primary Goals</span>
          <Textarea
            id="persona-goals"
            className="w-full bg-gray-50 resize-none min-h-[120px] text-base border border-gray-200 rounded text-gray-700 focus:ring-2 focus:ring-black focus:border-black"
            value={editFields.primaryGoals}
            onChange={e => handleEditFieldChange("primaryGoals", e.target.value)}
            placeholder={"List or write the persona's goals (use bullet points or plain text)"}
            rows={7}
          />
        </div>
        {/* Buttons positioned at bottom right of the grid */}
        <div className="flex justify-end space-x-3 pt-4">
          <Button 
            id="persona-delete-button"
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700" 
            size="sm" 
            variant="destructive" 
            onClick={handleDelete}
          >
            Delete
          </Button>
          <Button className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800" size="sm" variant="default" onClick={handleSave}>Save</Button>
        </div>
      </div>
    </div>
  );
} 