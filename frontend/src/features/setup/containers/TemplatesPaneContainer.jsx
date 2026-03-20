import { useState } from 'react'
import { toSqlFromDayjs } from '../utils/templatesPaneUtils'

import { useTemplatesPaneState, useKeyOptions } from '../hooks/useTemplatesPaneState'
import { useSchedules } from '../hooks/useSchedules'
import { useDiscoveryAndGeneration } from '../hooks/useDiscoveryAndGeneration'
import TemplatesPaneHeader from '../components/TemplatesPaneHeader'
import TemplatesPaneTabs from '../components/TemplatesPaneTabs'
import ConfigureTab from '../components/ConfigureTab'
import SchedulesTab from '../components/SchedulesTab'
import ScheduleDialogs from '../components/ScheduleDialogs'

export default function TemplatesPane() {
  const state = useTemplatesPaneState()
  const [keyValues, setKeyValues] = useState({})
  const [keyOptions, setKeyOptions] = useState({})
  const [keyOptionsLoading, setKeyOptionsLoading] = useState({})

  const keyState = useKeyOptions({
    selectedTemplates: state.selectedTemplates,
    activeConnectionId: state.activeConnectionId,
    discoveryMeta: state.discoveryMeta,
    toast: state.toast,
    start: state.start,
    end: state.end,
    keyOptions,
    setKeyOptions,
    keyValues,
    setKeyValues,
    keyOptionsLoading,
    setKeyOptionsLoading,
  })

  const disc = useDiscoveryAndGeneration({
    selectedTemplates: state.selectedTemplates,
    selected: state.selected,
    start: state.start,
    end: state.end,
    activeConnectionId: state.activeConnectionId,
    activeConnection: state.activeConnection,
    autoType: state.autoType,
    finding: state.finding,
    setFinding: state.setFinding,
    results: state.results,
    setDiscoveryResults: state.setDiscoveryResults,
    clearDiscoveryResults: state.clearDiscoveryResults,
    toast: state.toast,
    execute: state.execute,
    buildKeyFiltersForTemplate: keyState.buildKeyFiltersForTemplate,
    requestKeyOptions: keyState.requestKeyOptions,
    keysReady: keyState.keysReady,
    collectMissingKeys: keyState.collectMissingKeys,
    keyOptionsFetchKeyRef: keyState.keyOptionsFetchKeyRef,
    emailTargets: state.emailTargets,
    emailSubject: state.emailSubject,
    emailMessage: state.emailMessage,
  })

  const sched = useSchedules({ toast: state.toast, execute: state.execute })

  const dateRangeValid = !!state.start && !!state.end && state.end.valueOf() >= state.start.valueOf()
  const hasResults = Object.keys(state.results).length > 0
  const batchCount = Object.values(state.results).reduce(
    (acc, r) => acc + (r.batches?.filter(b => b.selected)?.length || 0), 0,
  )

  const onCreateSchedule = () => {
    sched.handleCreateSchedule({
      selectedTemplates: state.selectedTemplates,
      start: state.start,
      end: state.end,
      activeConnectionId: state.activeConnectionId,
      startSql: toSqlFromDayjs(state.start),
      endSql: toSqlFromDayjs(state.end),
      buildKeyFiltersForTemplate: keyState.buildKeyFiltersForTemplate,
      batchIdsFor: disc.batchIdsFor,
      emailTargets: state.emailTargets,
      emailSubject: state.emailSubject,
      emailMessage: state.emailMessage,
    })
  }

  return (
    <>
      <TemplatesPaneHeader
        selected={state.selected}
        dateRangeValid={dateRangeValid}
        hasResults={hasResults}
        batchCount={batchCount}
        finding={state.finding}
        onFind={disc.onFind}
        onGenerate={disc.onGenerate}
        canGenerate={disc.canGenerate}
        generateLabel={disc.generateLabel}
      />

      <TemplatesPaneTabs
        activeTab={state.activeTab}
        handleTabChange={state.handleTabChange}
        selectedCount={state.selected.length}
        schedulesCount={sched.schedules.length}
        selected={state.selected}
        onToggle={state.onToggle}
        outputFormats={state.outputFormats}
        setOutputFormats={state.setOutputFormats}
        tagFilter={state.tagFilter}
        setTagFilter={state.setTagFilter}
        handleNavigate={state.handleNavigate}
        configureContent={
          <ConfigureTab
            selected={state.selected}
            selectedTemplates={state.selectedTemplates}
            autoType={state.autoType}
            start={state.start}
            end={state.end}
            setStart={state.setStart}
            setEnd={state.setEnd}
            onFind={disc.onFind}
            finding={state.finding}
            results={state.results}
            onToggleBatch={disc.onToggleBatch}
            onGenerate={disc.onGenerate}
            canGenerate={disc.canGenerate}
            generateLabel={disc.generateLabel}
            generation={disc.generation}
            keyValues={keyValues}
            onKeyValueChange={keyState.handleKeyValueChange}
            keysReady={keyState.keysReady}
            keyOptions={keyOptions}
            keyOptionsLoading={keyOptionsLoading}
            onResampleFilter={disc.handleResampleFilter}
            queuedJobs={disc.queuedJobs}
            queuedJobIds={disc.queuedJobIds}
            handleNavigate={state.handleNavigate}
            emailTargets={state.emailTargets}
            setEmailTargets={state.setEmailTargets}
            emailSubject={state.emailSubject}
            setEmailSubject={state.setEmailSubject}
            emailMessage={state.emailMessage}
            setEmailMessage={state.setEmailMessage}
          />
        }
        schedulesContent={
          <SchedulesTab
            schedules={sched.schedules}
            schedulesLoading={sched.schedulesLoading}
            scheduleSaving={sched.scheduleSaving}
            deletingScheduleId={sched.deletingScheduleId}
            scheduleName={sched.scheduleName}
            setScheduleName={sched.setScheduleName}
            scheduleFrequency={sched.scheduleFrequency}
            setScheduleFrequency={sched.setScheduleFrequency}
            canSchedule={disc.canSchedule}
            onCreateSchedule={onCreateSchedule}
            handleDeleteScheduleRequest={sched.handleDeleteScheduleRequest}
            handleOpenEditSchedule={sched.handleOpenEditSchedule}
          />
        }
      />

      <ScheduleDialogs
        editingSchedule={sched.editingSchedule}
        editScheduleFields={sched.editScheduleFields}
        setEditScheduleFields={sched.setEditScheduleFields}
        scheduleUpdating={sched.scheduleUpdating}
        handleCloseEditSchedule={sched.handleCloseEditSchedule}
        handleUpdateSchedule={sched.handleUpdateSchedule}
        deleteScheduleConfirmOpen={sched.deleteScheduleConfirmOpen}
        setDeleteScheduleConfirmOpen={sched.setDeleteScheduleConfirmOpen}
        scheduleToDelete={sched.scheduleToDelete}
        setScheduleToDelete={sched.setScheduleToDelete}
        deletingScheduleId={sched.deletingScheduleId}
        handleDeleteScheduleConfirm={sched.handleDeleteScheduleConfirm}
      />
    </>
  )
}
