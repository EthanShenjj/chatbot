'use client'

import React, { useEffect, useRef, useState } from 'react';
import { ChevronDown, Settings, Plus, Trash2, Check, KeyRound, X } from 'lucide-react';
import { useModelStore } from '@/stores/modelStore';
import type { ModelConfigForm } from '@/types/model';

const EMPTY_FORM: ModelConfigForm = { name: '', model_id: '', base_url: '', api_key: '' };

const MODEL_TEMPLATES = [
  {
    name: 'OpenAI GPT-4o',
    model_id: 'gpt-4o',
    base_url: 'https://api.openai.com/v1/chat/completions',
  },
  {
    name: 'OpenAI GPT-4o Mini',
    model_id: 'gpt-4o-mini',
    base_url: 'https://api.openai.com/v1/chat/completions',
  },
  {
    name: 'Claude 3.5 Sonnet',
    model_id: 'claude-3-5-sonnet-20241022',
    base_url: 'https://api.anthropic.com/v1/messages',
  },
];

export const ModelSelector: React.FC = () => {
  const { models, selectedModelId, isLoading, fetchModels, selectModel, createModel, updateModel, deleteModel } =
    useModelStore();

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<ModelConfigForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const selectedModel = models.find((m) => m.id === selectedModelId);

  const openEdit = (id: string) => {
    const m = models.find((m) => m.id === id);
    if (!m) return;
    setForm({ id: m.id, name: m.name, model_id: m.model_id, base_url: m.base_url, api_key: '' });
    setEditingId(id);
  };

  const openCreate = () => {
    setForm(EMPTY_FORM);
    setEditingId('__new__');
  };

  const handleSave = async () => {
    if (!form.name || !form.model_id || !form.base_url) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    
    try {
      if (editingId === '__new__') {
        await createModel(form);
        setSuccess('Model created successfully!');
      } else if (editingId) {
        await updateModel(editingId, form);
        setSuccess('Model updated successfully!');
      }
      
      // Clear form and close after a short delay
      setTimeout(() => {
        setEditingId(null);
        setForm(EMPTY_FORM);
        setSuccess(null);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save model');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!editingId || editingId === '__new__') return;
    
    if (!confirm('Are you sure you want to delete this model?')) return;
    
    setSaving(true);
    setError(null);
    
    try {
      await deleteModel(editingId);
      setSuccess('Model deleted successfully!');
      setTimeout(() => {
        setEditingId(null);
        setForm(EMPTY_FORM);
        setSuccess(null);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete model');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      {/* Selector button */}
      <div className="relative flex items-center gap-1" ref={dropdownRef}>
        <button
          onClick={() => setDropdownOpen((v) => !v)}
          className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
        >
          <span>{isLoading ? 'Loading…' : (selectedModel?.name ?? 'Select model')}</span>
          <ChevronDown size={14} className="text-slate-400" />
        </button>

        <button
          onClick={() => setSettingsOpen(true)}
          className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
          title="Configure models"
        >
          <Settings size={14} className="text-slate-400" />
        </button>

        {/* Dropdown */}
        {dropdownOpen && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setDropdownOpen(false)} />
            <div className="absolute left-0 mt-2 w-64 bg-white border border-slate-200 rounded-xl shadow-xl z-20 overflow-hidden py-1">
              <div className="px-3 py-2 border-b border-slate-50">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Switch Model</span>
              </div>
              <div className="max-h-60 overflow-y-auto custom-scrollbar">
                {models.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => { selectModel(m.id); setDropdownOpen(false); }}
                    className={`w-full flex items-center justify-between px-4 py-2.5 text-sm transition-colors ${
                      m.id === selectedModelId ? 'bg-blue-50 text-[#137fec] font-medium' : 'text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="truncate">{m.name}</span>
                    </div>
                    {m.id === selectedModelId && <div className="w-1.5 h-1.5 rounded-full bg-[#137fec]" />}
                  </button>
                ))}
              </div>
              <div className="p-2 border-t border-slate-50">
                <button
                  onClick={() => { setDropdownOpen(false); setSettingsOpen(true); }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-slate-500 hover:bg-slate-50 rounded-lg transition-colors"
                >
                  <Settings size={14} />
                  Manage Models
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Settings modal */}
      {settingsOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#f1f5f9]">
              <h2 className="text-[16px] font-semibold text-[#0f172a]">Model Configuration</h2>
              <button onClick={() => { setSettingsOpen(false); setEditingId(null); }} className="p-1.5 hover:bg-slate-100 rounded-lg">
                <X size={16} className="text-slate-500" />
              </button>
            </div>

            <div className="flex divide-x divide-[#f1f5f9]" style={{ minHeight: 320 }}>
              {/* Model list */}
              <div className="w-48 shrink-0 py-2 overflow-y-auto">
                {models.map((m) => (
                  <div
                    key={m.id}
                    onClick={() => openEdit(m.id)}
                    className={`flex items-center gap-2 px-4 py-2.5 cursor-pointer transition-colors ${
                      editingId === m.id ? 'bg-[rgba(19,127,236,0.08)] text-[#137fec]' : 'hover:bg-slate-50 text-[#475569]'
                    }`}
                  >
                    <span className="text-[13px] font-medium truncate flex-1">{m.name}</span>
                    {!m.has_api_key && <KeyRound size={11} className="text-amber-400 shrink-0" />}
                  </div>
                ))}
                <button
                  onClick={openCreate}
                  className="w-full flex items-center gap-2 px-4 py-2.5 text-[13px] text-[#64748b] hover:bg-slate-50 transition-colors"
                >
                  <Plus size={13} /> Add model
                </button>
              </div>

              {/* Edit form */}
              <div className="flex-1 p-5">
                {error && (
                  <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-[12px] text-red-600">
                    {error}
                  </div>
                )}
                
                {success && (
                  <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg text-[12px] text-green-600 flex items-center gap-2">
                    <Check size={14} />
                    {success}
                  </div>
                )}
                
                {editingId ? (
                  <ModelForm
                    form={form}
                    onChange={setForm}
                    onSave={handleSave}
                    onCancel={() => { setEditingId(null); setForm(EMPTY_FORM); setError(null); }}
                    onDelete={editingId !== '__new__' ? handleDelete : undefined}
                    saving={saving}
                    isNew={editingId === '__new__'}
                  />
                ) : (
                  <div className="h-full flex items-center justify-center text-[13px] text-slate-400">
                    Select a model to edit or click "Add model" to create a new one
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

interface ModelFormProps {
  form: ModelConfigForm;
  onChange: (f: ModelConfigForm) => void;
  onSave: () => void;
  onCancel: () => void;
  onDelete?: () => void;
  saving: boolean;
  isNew: boolean;
}

const ModelForm: React.FC<ModelFormProps> = ({ form, onChange, onSave, onCancel, onDelete, saving, isNew }) => {
  const [showTemplates, setShowTemplates] = useState(false);

  const field = (label: string, key: keyof ModelConfigForm, placeholder: string, type = 'text', helpText?: string) => (
    <div className="space-y-1">
      <label className="text-[12px] font-medium text-[#64748b]">{label}</label>
      <input
        type={type}
        value={form[key]}
        onChange={(e) => onChange({ ...form, [key]: e.target.value })}
        placeholder={placeholder}
        className="w-full border border-[#e2e8f0] rounded-lg px-3 py-2 text-[13px] text-[#0f172a] placeholder:text-slate-300 outline-none focus:border-[#137fec] transition-colors"
      />
      {helpText && <p className="text-[11px] text-slate-400">{helpText}</p>}
    </div>
  );

  const applyTemplate = (template: typeof MODEL_TEMPLATES[0]) => {
    onChange({
      ...form,
      name: template.name,
      model_id: template.model_id,
      base_url: template.base_url,
    });
    setShowTemplates(false);
  };

  return (
    <div className="space-y-3">
      {isNew && (
        <div className="mb-3">
          <button
            onClick={() => setShowTemplates(!showTemplates)}
            className="text-[12px] text-[#137fec] hover:text-[#0f6ed8] font-medium flex items-center gap-1"
          >
            <Plus size={12} />
            {showTemplates ? 'Hide templates' : 'Use a template'}
          </button>
          
          {showTemplates && (
            <div className="mt-2 space-y-1">
              {MODEL_TEMPLATES.map((template, idx) => (
                <button
                  key={idx}
                  onClick={() => applyTemplate(template)}
                  className="w-full text-left px-3 py-2 text-[12px] bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  <div className="font-medium text-slate-900">{template.name}</div>
                  <div className="text-slate-500">{template.model_id}</div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {field('Display Name', 'name', 'e.g. My GPT-4', 'text', 'A friendly name for this model')}
      {field('Model ID', 'model_id', 'e.g. gpt-4o', 'text', 'The model identifier from the provider')}
      {field('Base URL', 'base_url', 'https://api.openai.com/v1/chat/completions', 'text', 'The API endpoint URL')}
      {field('API Key', 'api_key', isNew ? 'sk-…' : '(leave blank to keep existing)', 'password', isNew ? 'Your API key from the provider' : 'Leave blank to keep the existing key')}

      <div className="flex items-center justify-between pt-2">
        {onDelete ? (
          <button onClick={onDelete} className="flex items-center gap-1.5 text-[12px] text-red-400 hover:text-red-600 transition-colors">
            <Trash2 size={13} /> Delete
          </button>
        ) : <span />}
        <div className="flex gap-2">
          <button onClick={onCancel} className="px-3 py-1.5 text-[13px] text-slate-500 hover:bg-slate-100 rounded-lg transition-colors">
            Cancel
          </button>
          <button
            onClick={onSave}
            disabled={saving || !form.name || !form.model_id || !form.base_url}
            className="px-4 py-1.5 text-[13px] font-semibold bg-[#137fec] text-white rounded-lg hover:bg-[#0f6ed8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};
