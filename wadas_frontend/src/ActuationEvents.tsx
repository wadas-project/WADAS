import React, { useEffect, useMemo, useCallback, useState } from "react";
import { Alert, Button, Col, Container, Modal, Row } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import Select, { MultiValue } from "react-select";
import { useNavigate } from "react-router-dom";

import CustomNavbar from "./components/CustomNavbar";
import DatePick from "./components/DatePick";
import CustomSpinner from "./components/CustomSpinner";
import ActuationsScrollableTable from "./components/ActuationsScrollableTable";
import ActuationsMobileList from "./components/ActuationsMobileList";

import { isMobile, tryWithRefreshing } from "./lib/utils";
import {
  fetchActuationEvents,
  fetchActuatorTypes,
  fetchCommands,
  fetchExportActuationEvents,
} from "./lib/api";

import {
  ActuationEvent,
  ActuationEventResponse,
  ActuatorTypesResponse,
  CommandsResponse,
} from "./types/types";

type ActuatorTypeOption = {
  value: string;
  label: string;
};

type CommandOption = {
  value: string;
  label: string;
};

const getErrorMessage = (e: unknown) =>
  e instanceof Error ? e.message : String(e);

type Filters = {
  actuatorTypes: string[];
  commands: string[];
  startDate: Date | null;
  endDate: Date | null;
};

type ActuationFiltersProps = {
  actuatorTypeOptions: ActuatorTypeOption[];
  commandOptions: CommandOption[];
  selectedActuatorType: MultiValue<ActuatorTypeOption>;
  selectedCommand: MultiValue<CommandOption>;
  onChangeActuatorType: (v: MultiValue<ActuatorTypeOption>) => void;
  onChangeCommand: (v: MultiValue<CommandOption>) => void;
  startDate: Date | null;
  endDate: Date | null;
  onDateChange: (dates: [Date | null, Date | null]) => void;

  onApply: () => void;

  exportLoading: boolean;
  exportError: string | null;
  onExport: () => void;

  layout: "desktop" | "mobile";
};

const ActuationFilters: React.FC<ActuationFiltersProps> = ({
  actuatorTypeOptions,
  commandOptions,
  selectedActuatorType,
  selectedCommand,
  onChangeActuatorType,
  onChangeCommand,
  startDate,
  endDate,
  onDateChange,
  onApply,
  exportLoading,
  exportError,
  onExport,
  layout,
}) => {
  const actuatorPlaceholder = (
    <div className={"custom-placeholder"}>select actuator types...</div>
  );
  const commandPlaceholder = (
    <div className={"custom-placeholder"}>select actuation commands...</div>
  );

  if (layout === "desktop") {
    return (
      <Container className="mt-3">
        <Row className="mb-3">
          <Col md={3}>
            <Select
              instanceId="actuator-types-select"
              isMulti
              options={actuatorTypeOptions}
              value={selectedActuatorType}
              onChange={onChangeActuatorType}
              placeholder={actuatorPlaceholder}
            />
          </Col>

          <Col md={3}>
            <Select
              instanceId="commands-select"
              isMulti
              options={commandOptions}
              value={selectedCommand}
              onChange={onChangeCommand}
              placeholder={commandPlaceholder}
            />
          </Col>

          <Col md={3}>
            <DatePick startDate={startDate} endDate={endDate} onDateChange={onDateChange} />
          </Col>

          <Col md={1}>
            <Button
              variant="primary"
              className="custom-button dark-background"
              onClick={onApply}
            >
              Apply
            </Button>
          </Col>

          <Col md={2} className="d-flex">
            {exportLoading ? (
              <CustomSpinner className={"mt-1 ms-auto me-5"} />
            ) : exportError ? (
              <Alert variant="danger" className={"m-0 p-2"} style={{ fontSize: "12px" }}>
                {exportError}
              </Alert>
            ) : (
              <Button variant="primary" className="custom-button ms-auto" onClick={onExport}>
                Export results
              </Button>
            )}
          </Col>
        </Row>
      </Container>
    );
  }

  // mobile layout (inside modal body)
  return (
    <>
      <Select
        instanceId="actuator-types-select-mobile"
        isMulti
        options={actuatorTypeOptions}
        value={selectedActuatorType}
        onChange={onChangeActuatorType}
        placeholder={actuatorPlaceholder}
      />

      <Select
        instanceId="commands-select-mobile"
        isMulti
        options={commandOptions}
        value={selectedCommand}
        onChange={onChangeCommand}
        placeholder={commandPlaceholder}
        className="mt-3"
        styles={{
          container: (baseStyles) => ({
            ...baseStyles,
            marginBottom: "1rem",
          }),
        }}
      />

      <DatePick startDate={startDate} endDate={endDate} onDateChange={onDateChange} />

      <Button
        variant="primary"
        className="custom-button dark-background"
        style={{ marginTop: "1rem" }}
        onClick={onApply}
      >
        Apply
      </Button>

      <div style={{ marginTop: "1rem" }}>
        {exportLoading ? (
          <CustomSpinner />
        ) : exportError ? (
          <Alert variant="danger" className={"m-0 p-2"} style={{ fontSize: "12px" }}>
            {exportError}
          </Alert>
        ) : (
          <Button variant="primary" className="custom-button" onClick={onExport}>
            Export results
          </Button>
        )}
      </div>
    </>
  );
};

const ActuationEvents: React.FC = () => {
  const pageSize = 20;

  const [showFilters, setShowFilters] = useState(false);

  const [actuatorTypeOptions, setActuatorTypeOptions] = useState<ActuatorTypeOption[]>([]);
  const [commandOptions, setCommandOptions] = useState<CommandOption[]>([]);

  const [actuations, setActuations] = useState<ActuationEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [tableLoading, setTableLoading] = useState<boolean>(false);

  const [exportLoading, setExportLoading] = useState<boolean>(false);

  const [selectedActuatorType, setSelectedActuatorType] = useState<
    MultiValue<ActuatorTypeOption>
  >([]);
  const [selectedCommand, setSelectedCommand] = useState<MultiValue<CommandOption>>([]);

  const [error, setError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

  const [mobileFlag, setMobileFlag] = useState(isMobile());

  const navigate = useNavigate();

  // Keep mobileFlag updated on resize/orientation changes
  useEffect(() => {
    const onResize = () => setMobileFlag(isMobile());
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const updateDateRange = useCallback((dates: [Date | null, Date | null]) => {
    const [start, end] = dates;
    setStartDate(start);
    setEndDate(end);
  }, []);

  const currentFilters: Filters = useMemo(
    () => ({
      actuatorTypes: selectedActuatorType.map((x) => x.value),
      commands: selectedCommand.map((x) => x.value),
      startDate,
      endDate,
    }),
    [selectedActuatorType, selectedCommand, startDate, endDate]
  );

  const handleUnauthorizedOrGeneric = useCallback(
    (e: unknown, setter?: (msg: string) => void) => {
      const msg = getErrorMessage(e);
      if (msg.includes("Unauthorized")) {
        console.error("Refresh token failed, redirecting to login...");
        navigate("/");
        return;
      }
      setter?.(msg);
    },
    [navigate]
  );

  const loadActuations = useCallback(
    async ({
      page = 1,
      filters = currentFilters,
      showGlobalSpinner = false,
    }: {
      page?: number;
      filters?: Filters;
      showGlobalSpinner?: boolean;
    } = {}) => {
      const offset = (page - 1) * pageSize;

      if (showGlobalSpinner) setLoading(true);
      else setTableLoading(true);

      setError(null);

      try {
        const actuationsResponse: ActuationEventResponse = await tryWithRefreshing(() =>
          fetchActuationEvents(
            offset,
            null,
            filters.actuatorTypes,
            filters.commands,
            filters.startDate,
            filters.endDate
          )
        );

        setActuations(actuationsResponse.data);
        setTotalPages(Math.ceil(actuationsResponse.total / pageSize));
        setCurrentPage(page);
      } catch (e) {
        handleUnauthorizedOrGeneric(e, (msg) =>
          setError(`Generic Error - ${msg}. Please contact the administrator.`)
        );
      } finally {
        if (showGlobalSpinner) setLoading(false);
        else setTableLoading(false);
      }
    },
    [currentFilters, handleUnauthorizedOrGeneric]
  );

  const loadStaticOptionsAndFirstPage = useCallback(async () => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    try {
      const [actuatorTypesResponse, commandsResponse]: [
        ActuatorTypesResponse,
        CommandsResponse
      ] = await Promise.all([
        tryWithRefreshing(fetchActuatorTypes),
        tryWithRefreshing(fetchCommands),
      ]);

      if (cancelled) return;

      setActuatorTypeOptions(
        actuatorTypesResponse.data.map((x) => ({
          value: x,
          label: x,
        }))
      );

      setCommandOptions(
        commandsResponse.data.map((x) => ({
          value: x,
          label: x,
        }))
      );

      await loadActuations({ page: 1, showGlobalSpinner: true });
    } catch (e) {
      handleUnauthorizedOrGeneric(e, (msg) =>
        setError(`Generic Error - ${msg}. Please contact the administrator.`)
      );
    } finally {
      if (!cancelled) setLoading(false);
    }

    return () => {
      cancelled = true;
    };
  }, [handleUnauthorizedOrGeneric, loadActuations]);

  // Initial load
  useEffect(() => {
    let cancelled = false;

    (async () => {
      setLoading(true);
      setError(null);

      try {
        const [actuatorTypesResponse, commandsResponse]: [
          ActuatorTypesResponse,
          CommandsResponse
        ] = await Promise.all([
          tryWithRefreshing(fetchActuatorTypes),
          tryWithRefreshing(fetchCommands),
        ]);

        if (cancelled) return;

        setActuatorTypeOptions(
          actuatorTypesResponse.data.map((x) => ({ value: x, label: x }))
        );
        setCommandOptions(commandsResponse.data.map((x) => ({ value: x, label: x })));

        await loadActuations({ page: 1, showGlobalSpinner: true });
      } catch (e) {
        handleUnauthorizedOrGeneric(e, (msg) =>
          setError(`Generic Error - ${msg}. Please contact the administrator.`)
        );
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChangeActuatorType = useCallback(
    (selected: MultiValue<ActuatorTypeOption>) => {
      setSelectedActuatorType(selected);
    },
    []
  );

  const handleChangeCommand = useCallback((selected: MultiValue<CommandOption>) => {
    setSelectedCommand(selected);
  }, []);

  const onApplyFilters = useCallback(() => {
    // Always reset page when applying new filters
    loadActuations({ page: 1 });
  }, [loadActuations]);

  const onExport = useCallback(async () => {
    setExportLoading(true);
    setExportError(null);

    try {
      const responseBlob: Blob = await tryWithRefreshing(() =>
        fetchExportActuationEvents(
          null,
          currentFilters.actuatorTypes,
          currentFilters.commands,
          currentFilters.startDate,
          currentFilters.endDate
        )
      );

      const url = window.URL.createObjectURL(responseBlob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "actuation_events.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      const msg = getErrorMessage(e);
      if (msg.includes("Unauthorized")) {
        console.error("Refresh token failed, redirecting to login...");
        navigate("/");
      } else {
        setExportError("Problem exporting data");
      }
    } finally {
      setExportLoading(false);
    }
  }, [currentFilters, navigate]);

  const content = useMemo(() => {
    if (loading) {
      return (
        <Container style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <CustomSpinner />
        </Container>
      );
    }

    if (error) {
      return <Alert variant="danger">{error}</Alert>;
    }

    if (!mobileFlag) {
      // Desktop view
      return (
        <Container style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <Container style={{ display: "flex", flexDirection: "column" }}>
            <ActuationFilters
              layout="desktop"
              actuatorTypeOptions={actuatorTypeOptions}
              commandOptions={commandOptions}
              selectedActuatorType={selectedActuatorType}
              selectedCommand={selectedCommand}
              onChangeActuatorType={handleChangeActuatorType}
              onChangeCommand={handleChangeCommand}
              startDate={startDate}
              endDate={endDate}
              onDateChange={updateDateRange}
              onApply={onApplyFilters}
              exportLoading={exportLoading}
              exportError={exportError}
              onExport={onExport}
            />

            <Container style={{ flex: 1, overflow: "hidden" }}>
              {tableLoading ? (
                <Container style={{ paddingTop: "1rem" }}>
                  <CustomSpinner />
                </Container>
              ) : null}

              <ActuationsScrollableTable
                actuations={actuations}
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={(page: number) => loadActuations({ page })}
              />
            </Container>
          </Container>
        </Container>
      );
    }

    // Mobile view
    return (
      <Container>
        <Row className="mb-3 mt-3 d-flex align-items-center">
          <Col xs={8}>
            <h3>Actuation Events</h3>
          </Col>
          <Col xs={4} className="d-flex justify-content-end">
            <Button
              variant="primary"
              className="custom-button dark-background"
              onClick={() => setShowFilters(true)}
            >
              Filter
            </Button>
          </Col>
        </Row>

        <Modal show={showFilters} onHide={() => setShowFilters(false)}>
          <Modal.Header closeButton>
            <Modal.Title>Filters</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <ActuationFilters
              layout="mobile"
              actuatorTypeOptions={actuatorTypeOptions}
              commandOptions={commandOptions}
              selectedActuatorType={selectedActuatorType}
              selectedCommand={selectedCommand}
              onChangeActuatorType={handleChangeActuatorType}
              onChangeCommand={handleChangeCommand}
              startDate={startDate}
              endDate={endDate}
              onDateChange={updateDateRange}
              onApply={() => {
                onApplyFilters();
                setShowFilters(false);
              }}
              exportLoading={exportLoading}
              exportError={exportError}
              onExport={onExport}
            />
          </Modal.Body>
        </Modal>

        {tableLoading ? (
          <Container style={{ paddingTop: "1rem" }}>
            <CustomSpinner />
          </Container>
        ) : null}

        <ActuationsMobileList
          actuations={actuations}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={(page: number) => loadActuations({ page })}
        />
      </Container>
    );
  }, [
    loading,
    error,
    mobileFlag,
    actuatorTypeOptions,
    commandOptions,
    selectedActuatorType,
    selectedCommand,
    startDate,
    endDate,
    updateDateRange,
    onApplyFilters,
    exportLoading,
    exportError,
    onExport,
    actuations,
    currentPage,
    totalPages,
    loadActuations,
    tableLoading,
    showFilters,
    handleChangeActuatorType,
    handleChangeCommand,
  ]);

  return (
    <div className={"padded-div"}>
      <CustomNavbar />
      <Container className={"mt-1"}>{content}</Container>
    </div>
  );
};

export default ActuationEvents;

