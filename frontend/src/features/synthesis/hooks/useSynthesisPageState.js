/**
 * Custom hook: all state + effects + handlers for SynthesisPage
 */
import { useState, useEffect, useCallback } from 'react';
import useSynthesisStore from '@/stores/synthesisStore';
import useSharedData from '@/hooks/useSharedData';
import useCrossPageActions from '@/hooks/useCrossPageActions';
import { OutputType, FeatureKey } from '@/utils/crossPageTypes';
import { useToast } from '@/components/ToastProvider';
import {
  useInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance';
import { extractDocument as extractSynthesisDocument } from '@/api/synthesis';

const MAX_DOC_SIZE = 5 * 1024 * 1024;
const MIN_DOC_LENGTH = 10;
const MAX_NAME_LENGTH = 200;
const MAX_FOCUS_TOPICS = 10;

export function useSynthesisPageState() {
  const {
    sessions,
    currentSession,
    inconsistencies,
    synthesisResult,
    loading,
    error,
    fetchSessions,
    createSession,
    getSession,
    deleteSession,
    addDocument,
    removeDocument,
    findInconsistencies,
    synthesize,
    reset,
  } = useSynthesisStore();

  const { connections, templates, activeConnectionId } = useSharedData();
  const { registerOutput } = useCrossPageActions(FeatureKey.SYNTHESIS);
  const [selectedConnectionId, setSelectedConnectionId] = useState(activeConnectionId);

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [addDocDialogOpen, setAddDocDialogOpen] = useState(false);
  const [newSessionName, setNewSessionName] = useState('');
  const [docName, setDocName] = useState('');
  const [docContent, setDocContent] = useState('');
  const [docType, setDocType] = useState('text');
  const [outputFormat, setOutputFormat] = useState('structured');
  const [focusTopics, setFocusTopics] = useState('');
  const [previewDoc, setPreviewDoc] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [deleteSessionConfirm, setDeleteSessionConfirm] = useState({ open: false, sessionId: null, sessionName: '' });
  const [removeDocConfirm, setRemoveDocConfirm] = useState({ open: false, docId: null, docName: '' });
  const toast = useToast();
  const docCount = currentSession?.documents?.length || 0;
  const { execute } = useInteraction();

  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      setInitialLoading(true);
      await fetchSessions();
      setInitialLoading(false);
    };
    init();
    return () => reset();
  }, [fetchSessions, reset]);

  const handleCreateSession = () => {
    if (!newSessionName) return;
    if (newSessionName.length > MAX_NAME_LENGTH) {
      toast.show(`Session name must be ${MAX_NAME_LENGTH} characters or less`, 'error');
      return;
    }
    execute({
      type: InteractionType.CREATE,
      label: `Create session "${newSessionName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Session created successfully',
      action: async () => {
        await createSession(newSessionName);
        setCreateDialogOpen(false);
        setNewSessionName('');
      },
    });
  };

  const handleAddDocument = () => {
    if (!currentSession || !docName || !docContent) return;
    if (docName.length > MAX_NAME_LENGTH) {
      toast.show(`Document name must be ${MAX_NAME_LENGTH} characters or less`, 'error');
      return;
    }
    if (docContent.trim().length < MIN_DOC_LENGTH) {
      toast.show(`Document content must be at least ${MIN_DOC_LENGTH} characters`, 'error');
      return;
    }
    if (docContent.length > MAX_DOC_SIZE) {
      toast.show('Document content exceeds 5MB limit', 'error');
      return;
    }
    execute({
      type: InteractionType.UPLOAD,
      label: `Add document "${docName}"`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Document added successfully',
      action: async () => {
        await addDocument(currentSession.id, {
          name: docName,
          content: docContent,
          docType,
        });
        setAddDocDialogOpen(false);
        setDocName('');
        setDocContent('');
      },
    });
  };

  const handleFileUpload = async (event) => {
    const inputEl = event.target;
    const file = inputEl.files?.[0];
    if (!file) return;
    if (file.name.length > MAX_NAME_LENGTH) {
      toast.show(`File name must be ${MAX_NAME_LENGTH} characters or less`, 'error');
      inputEl.value = '';
      return;
    }

    if (file.size > MAX_DOC_SIZE) {
      toast.show('File size exceeds 5MB limit', 'error');
      inputEl.value = '';
      return;
    }

    const ext = file.name.split('.').pop().toLowerCase();
    const inferredType = ext === 'pdf'
      ? 'pdf'
      : ['xlsx', 'xls', 'csv'].includes(ext)
        ? 'excel'
        : ['doc', 'docx'].includes(ext)
          ? 'word'
          : ext === 'json'
            ? 'json'
            : 'text';

    try {
      const response = await extractSynthesisDocument(file, { docType: inferredType });
      const extracted = response?.document;
      const content = extracted?.content || '';
      if (content.trim().length < MIN_DOC_LENGTH) {
        toast.show(`Extracted content must be at least ${MIN_DOC_LENGTH} characters`, 'error');
        inputEl.value = '';
        return;
      }

      setDocName(extracted?.name || file.name);
      setDocContent(content);
      setDocType(extracted?.doc_type || inferredType);
      if (extracted?.truncated) {
        toast.show('File content was truncated to fit 5MB limit', 'warning');
      } else {
        toast.show('File processed successfully', 'success');
      }
    } catch (err) {
      toast.show(err.message || 'Failed to process file', 'error');
    } finally {
      inputEl.value = '';
    }
  };

  const handleSynthesize = () => {
    if (!currentSession) return;
    const topics = focusTopics
      ? focusTopics.split(',').map((topic) => topic.trim()).filter(Boolean)
      : undefined;
    if (topics && topics.length > MAX_FOCUS_TOPICS) {
      toast.show(`Focus topics must be ${MAX_FOCUS_TOPICS} items or less`, 'error');
      return;
    }

    execute({
      type: InteractionType.GENERATE,
      label: 'Synthesize documents',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      successMessage: 'Synthesis complete',
      errorMessage: 'Synthesis failed',
      action: async () => {
        const result = await synthesize(currentSession.id, {
          focusTopics: topics,
          outputFormat,
          connectionId: selectedConnectionId || undefined,
        });
        if (!result) throw new Error('Synthesis failed');
        const synthTitle = result.synthesis?.title || currentSession.name || 'Synthesis';
        const synthContent = [
          result.synthesis?.executive_summary || '',
          ...(result.synthesis?.key_insights || []),
          ...(result.synthesis?.sections || []).map((s) => `${s.heading}\n${s.content}`),
        ].join('\n\n');
        registerOutput({
          type: OutputType.TEXT,
          title: synthTitle,
          summary: (result.synthesis?.executive_summary || '').substring(0, 200),
          data: synthContent,
          format: 'text',
        });
      },
    });
  };

  const handleFindInconsistencies = () => {
    if (!currentSession) return;
    execute({
      type: InteractionType.ANALYZE,
      label: 'Find inconsistencies',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      action: async () => {
        const result = await findInconsistencies(currentSession.id);
        if (result === null) throw new Error('Analysis failed');
        if (result.length > 0) {
          toast.show(`Found ${result.length} inconsistencies`, 'warning');
        } else {
          toast.show('No inconsistencies found', 'success');
        }
      },
    });
  };

  const handleOpenPreview = (doc) => {
    setPreviewDoc(doc);
    setPreviewOpen(true);
  };

  const handleClosePreview = () => {
    setPreviewOpen(false);
    setPreviewDoc(null);
  };

  const handleDeleteSessionConfirm = () => {
    const sessionId = deleteSessionConfirm.sessionId;
    const sessionName = deleteSessionConfirm.sessionName;
    setDeleteSessionConfirm({ open: false, sessionId: null, sessionName: '' });

    execute({
      type: InteractionType.DELETE,
      label: `Delete session "${sessionName}"`,
      reversibility: Reversibility.IRREVERSIBLE,
      successMessage: `Session "${sessionName}" deleted`,
      errorMessage: 'Failed to delete session',
      action: async () => {
        const success = await deleteSession(sessionId);
        if (!success) throw new Error('Delete failed');
      },
    });
  };

  const handleRemoveDocConfirm = () => {
    const docId = removeDocConfirm.docId;
    const removedDocName = removeDocConfirm.docName;
    setRemoveDocConfirm({ open: false, docId: null, docName: '' });

    execute({
      type: InteractionType.DELETE,
      label: `Remove document "${removedDocName}"`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      successMessage: `Document "${removedDocName}" removed`,
      errorMessage: 'Failed to remove document',
      action: async () => {
        const success = await removeDocument(currentSession?.id, docId);
        if (!success) throw new Error('Remove failed');
      },
    });
  };

  return {
    // Store state
    sessions,
    currentSession,
    inconsistencies,
    synthesisResult,
    loading,
    error,
    initialLoading,
    docCount,

    // Store actions
    getSession,
    reset,

    // Dialog state
    createDialogOpen,
    setCreateDialogOpen,
    addDocDialogOpen,
    setAddDocDialogOpen,
    newSessionName,
    setNewSessionName,
    docName,
    setDocName,
    docContent,
    setDocContent,
    docType,
    setDocType,
    outputFormat,
    setOutputFormat,
    focusTopics,
    setFocusTopics,
    previewDoc,
    previewOpen,
    deleteSessionConfirm,
    setDeleteSessionConfirm,
    removeDocConfirm,
    setRemoveDocConfirm,

    // Connection
    selectedConnectionId,
    setSelectedConnectionId,

    // Handlers
    handleCreateSession,
    handleAddDocument,
    handleFileUpload,
    handleSynthesize,
    handleFindInconsistencies,
    handleOpenPreview,
    handleClosePreview,
    handleDeleteSessionConfirm,
    handleRemoveDocConfirm,
  };
}
