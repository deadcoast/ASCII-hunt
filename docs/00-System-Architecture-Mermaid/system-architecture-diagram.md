```mermaid
graph TD
%% Import subgraphs and define cross-module dependencies
    %% Core System
    subgraph Core ["Core System"]
        direction TB
        %% Core nodes defined in core.mmd
    end

    %% DSL System
    subgraph DSL ["DSL Processing"]
        direction TB
        %% DSL nodes defined in dsl.mmd
    end

    %% Recognition System
    subgraph RecognitionSystem ["Component Recognition"]
        direction TB
        %% Recognition nodes defined in recognition.mmd
    end

    %% Modeling System
    subgraph Modeling ["Hierarchical Modeling"]
        direction TB
        %% Modeling nodes defined in modeling.mmd
    end

    %% Generation System
    subgraph Generation ["Code Generation"]
        direction TB
        %% Generation nodes defined in generation.mmd
    end

    %% Plugin System
    subgraph Plugins ["Plugin System"]
        direction TB
        %% Plugin nodes defined in plugins.mmd
    end

    %% Processing System
    subgraph Processing ["Processing System"]
        direction TB
        %% Processing nodes defined in processing.mmd
    end



%% Core System Components
ASCIIGrid["ASCIIGrid\n(hunt.core.grid)"]
Pipeline["ProcessingPipeline\n(hunt.core.pipeline)"]
CompModel["ComponentModel\n(hunt.core.model)"]
Persist["Persistence\n(hunt.core.persistence)"]
Registry["ComponentRegistry\n(hunt.core.registry)"]
Cache["CacheSystem\n(hunt.core.cache)"]
ErrorHandler["ErrorHandler\n(hunt.core.dsl.dsl_error)"]
ErrorProcessor["ErrorProcessor\n(hunt.core.dsl.dsl_error_handler)"]

%% Core Internal Dependencies
Pipeline --> ASCIIGrid
Pipeline --> CompModel
Pipeline --> Persist
Pipeline --> Registry
Pipeline --> Cache
CompModel --> Registry
CompModel --> Persist
ErrorHandler --> Pipeline
ErrorProcessor --> ErrorHandler
ErrorProcessor --> Pipeline

%% Apply core styles
class ASCIIGrid,Pipeline,CompModel,Persist,Registry,Cache,ErrorHandler,ErrorProcessor core;

%% DSL System Components
Lexer["Lexical Analyzer\n(hunt.dsl.lexer)"]
Parser["Syntax Parser\n(hunt.dsl.parser)"]
ASTGen["AST Generator\n(hunt.dsl.ast)"]
SemAnalyzer["Semantic Analyzer\n(hunt.dsl.semantic)"]
DslInterp["DslInterpreter\n(hunt.dsl.interpreter)"]
CmdDisp["CommandDispatcher\n(hunt.dsl.commands)"]
PatternDef["PatternDefinitions\n(hunt.dsl.patterns)"]
TmplEngine["TemplateEngine\n(hunt.dsl.templates)"]
Grammar["Grammar Rules\n(hunt.dsl.grammar)"]
Nodes["AST Nodes\n(hunt.dsl.nodes)"]
Evaluator["Expression Evaluator\n(hunt.dsl.evaluator)"]

%% DSL Internal Dependencies
Lexer --> Grammar
Parser --> Lexer
Parser --> Grammar
ASTGen --> Parser
ASTGen --> Nodes
SemAnalyzer --> ASTGen
DslInterp --> SemAnalyzer
DslInterp --> Evaluator
CmdDisp --> DslInterp
PatternDef --> CmdDisp
TmplEngine --> PatternDef

%% Apply DSL styles
class Lexer,Parser,ASTGen,SemAnalyzer,DslInterp,CmdDisp,PatternDef,TmplEngine,Grammar,Nodes,Evaluator dsl;

%% Recognition System Components
FloodFill["FloodFillProcessor\n(hunt.recognition.floodfill)"]
Contour["ContourDetector\n(hunt.recognition.contour)"]
Features["FeatureExtractor\n(hunt.recognition.features)"]
PatternMatch["PatternMatcher\n(hunt.recognition.matcher)"]
RuleEngine["RuleEngine\n(hunt.recognition.rules)"]
RecognitionMgr["RecognitionManager\n(hunt.recognition.manager)"]
Processing["ProcessingEngine\n(hunt.recognition.processing)"]
Training["TrainingSystem\n(hunt.recognition.training)"]

%% Recognition Internal Dependencies
RecognitionMgr --> FloodFill
RecognitionMgr --> Contour
RecognitionMgr --> Features
RecognitionMgr --> PatternMatch
RecognitionMgr --> RuleEngine
FloodFill --> ASCIIGrid
Contour --> ASCIIGrid
Features --> Contour
PatternMatch --> Features
PatternMatch --> RuleEngine
Processing --> RecognitionMgr
Training --> RecognitionMgr

%% Apply Recognition styles
class FloodFill,Contour,Features,PatternMatch,RuleEngine,RecognitionMgr,Processing,Training recog;

%% Modeling System Components
ContainAnalyzer["ContainmentAnalyzer\n(hunt.modeling.hierarchy)"]
LayoutAnalyzer["LayoutAnalyzer\n(hunt.modeling.layout)"]
RelationAnalyzer["RelationshipAnalyzer\n(hunt.modeling.relationships)"]
ModelBuilder["ModelBuilder\n(hunt.modeling.builder)"]
Spatial["SpatialAnalyzer\n(hunt.modeling.spatial)"]
Arrangement["ArrangementManager\n(hunt.modeling.arrangement)"]
Graph["GraphProcessor\n(hunt.modeling.graph)"]

%% Modeling Internal Dependencies
ModelBuilder --> ContainAnalyzer
ModelBuilder --> LayoutAnalyzer
ModelBuilder --> RelationAnalyzer
ModelBuilder --> Spatial
ContainAnalyzer --> CompModel
LayoutAnalyzer --> CompModel
RelationAnalyzer --> CompModel
Spatial --> Graph
Arrangement --> Graph

%% Apply Modeling styles
class ContainAnalyzer,LayoutAnalyzer,RelationAnalyzer,ModelBuilder,Spatial,Arrangement,Graph model;

%% Code Generation Components
Generator["CodeGenerator\n(hunt.generation.generator)"]
Templates["TemplateRegistry\n(hunt.generation.templates)"]
Adapters["FrameworkAdapters\n(hunt.generation.adapters)"]
PropMapper["PropertyMapper\n(hunt.generation.renderers)"]
TemplateEngine["TemplateProcessor\n(hunt.generation.template_engine)"]
CodeGenCore["CoreGenerator\n(hunt.generation.code_gen)"]
Renderers["RenderingEngine\n(hunt.generation.renderers)"]

%% Generation Internal Dependencies
Generator --> Templates
Generator --> Adapters
Generator --> TemplateEngine
Generator --> CodeGenCore
CodeGenCore --> Renderers
Adapters --> PropMapper
Templates --> TemplateEngine

%% Apply Generation styles
class Generator,Templates,Adapters,PropMapper,TemplateEngine,CodeGenCore,Renderers codegen;

%% Plugin System Components
PluginMgr["PluginManager\n(hunt.plugins.manager)"]
ExtRegistry["ExtensionRegistry\n(hunt.plugins.extension)"]
PluginReg["PluginRegistry\n(hunt.plugins.registry)"]
Discovery["PluginDiscovery\n(hunt.plugins.discovery)"]
Loader["PluginLoader\n(hunt.plugins.loader)"]
Points["ExtensionPoints\n(hunt.plugins.points)"]

%% Plugin Internal Dependencies
PluginMgr --> ExtRegistry
PluginMgr --> PluginReg
PluginMgr --> Discovery
Loader --> PluginMgr
Points --> ExtRegistry

%% Apply Plugin styles
class PluginMgr,ExtRegistry,PluginReg,Discovery,Loader,Points plugin;

%% Processing System Components
Transform["Transformations\n(processing.transform)"]
CompMapping["ComponentMapping\n(processing.transform.component_mapping)"]
OverlayMgr["ComponentOverlayManager\n(processing.transform.component_overlay)"]
FloodFillComp["FloodFillComponent\n(processing.transform.flood_fill)"]

Validation["Validation\n(processing.validation)"]
ClassProcessor["ComponentClassification\n(processing.validation.classification)"]

Analysis["Analysis\n(processing.analysis)"]
NeuroAnalysis["NeuromorphicAnalysis\n(processing.analysis.neuromorphic)"]

%% Processing Internal Dependencies
Transform --> CompMapping
Transform --> OverlayMgr
Transform --> FloodFillComp

Validation --> ClassProcessor
ClassProcessor --> NeuroAnalysis

Analysis --> NeuroAnalysis
CompMapping --> ClassProcessor
OverlayMgr --> ClassProcessor

%% Apply processing styles
class Transform,CompMapping,OverlayMgr,FloodFillComp,Validation,ClassProcessor,Analysis,NeuroAnalysis processing;

%% Pattern System Components
%% Definition Components
PatternLearner["PatternLearner\n(patterns.definitions.pattern_learner)"]
PatternMatcher["PatternMatcher\n(patterns.definitions.pattern_matcher)"]
PatternOptimizer["PatternOptimizer\n(patterns.definitions.pattern_optimizer)"]
CodeTemplate["CodeTemplate\n(patterns.definitions.code_template)"]
PropTemplate["ComponentPropsTemplate\n(patterns.definitions.component_props)"]
TkTemplate["TkMappingTemplate\n(patterns.definitions.tk_mapping)"]
ASCIIExamples["ASCIIExamples\n(patterns.definitions.ascii_examples)"]
TabExample["TabbedContentExample\n(patterns.definitions.tabbed_content)"]

%% Matching Components
FloodFillProc["FloodFillProcessor\n(patterns.matching.flood_fill)"]
GridTransform["GridTransformer\n(patterns.matching.grid_transformer)"]
HierarchicalCluster["HierarchicalClustering\n(patterns.matching.hierarchical)"]
ParsingAlgo["ParsingAlgorithms\n(patterns.matching.parsing)"]

%% Rules Components
DslParser["DslParser\n(patterns.rules.dsl_parser)"]
PatternRegistry["PatternRegistry\n(patterns.rules.pattern_registry)"]
RecognitionProc["RecognitionProcessor\n(patterns.rules.recognition)"]

%% Pattern Internal Dependencies
%% Definition Dependencies
PatternLearner --> ASCIIExamples
PatternMatcher --> PatternLearner
PatternOptimizer --> PatternMatcher
CodeTemplate --> PropTemplate
CodeTemplate --> TkTemplate
TabExample --> CodeTemplate

%% Matching Dependencies
FloodFillProc --> GridTransform
HierarchicalCluster --> FloodFillProc
ParsingAlgo --> HierarchicalCluster

%% Rules Dependencies
DslParser --> PatternRegistry
PatternRegistry --> RecognitionProc
RecognitionProc --> PatternMatcher
RecognitionProc --> FloodFillProc

%% Apply patterns styles
class PatternLearner,PatternMatcher,PatternOptimizer,CodeTemplate,PropTemplate,TkTemplate,ASCIIExamples,TabExample,FloodFillProc,GridTransform,HierarchicalCluster,ParsingAlgo,DslParser,PatternRegistry,RecognitionProc patterns;

%% Engine System Components
%% Analysis Components
Analysis["Analysis\n(engine.analysis)"]
CompAnalysis["ComponentAnalysis\n(engine.analysis.component_analysis)"]
CompAnalysis2["ComponentAnalysis2\n(engine.analysis.component_analysis_two)"]
SpatialAnalysis["SpatialAnalysis\n(engine.analysis.spatial_analysis)"]
TemporalReasoning["TemporalReasoning\n(engine.analysis.temporal_reasoning)"]
DecisionTree["DecisionTree\n(engine.analysis.decision_tree)"]
DTClassifier["DecisionTreeClassifier\n(engine.analysis.decision_tree_classifier)"]

%% Modeling Components
Modeling["Modeling\n(engine.modeling)"]
CompModel["ComponentModelRepresentation\n(engine.modeling.component_model)"]
CompProps["ComponentProperties\n(engine.modeling.component_properties)"]
DrawingMode["DrawingMode\n(engine.modeling.drawing_mode)"]

%% Pipeline Components
Pipeline["ProcessingPipeline\n(engine.pipeline)"]
ASCIIProc["ASCIIProcessor\n(engine.pipeline.ascii_processor)"]
ContourDetection["ContourDetection\n(engine.pipeline.contour_detection)"]
FeatureExtraction["FeatureExtraction\n(engine.pipeline.feature_extraction)"]
FloodFill["FloodFillProcessor\n(engine.pipeline.flood_fill)"]
Transform["TransformationPipeline\n(engine.pipeline.transformation)"]

%% Engine Internal Dependencies
%% Analysis Dependencies
Analysis --> CompAnalysis
Analysis --> CompAnalysis2
Analysis --> SpatialAnalysis
Analysis --> TemporalReasoning
Analysis --> DecisionTree
Analysis --> DTClassifier

CompAnalysis2 --> CompAnalysis
DecisionTree --> DTClassifier
SpatialAnalysis --> TemporalReasoning
CompAnalysis --> SpatialAnalysis

%% Pipeline Dependencies
Pipeline --> ASCIIProc
Pipeline --> ContourDetection
Pipeline --> FeatureExtraction
Pipeline --> FloodFill
Pipeline --> Transform

ASCIIProc --> FloodFill
ContourDetection --> FloodFill
FeatureExtraction --> ContourDetection
Transform --> FeatureExtraction

%% Modeling Dependencies
Modeling --> CompModel
Modeling --> CompProps
Modeling --> DrawingMode

CompProps --> CompModel
DrawingMode --> CompModel

%% Cross-component Dependencies
CompAnalysis --> Pipeline
TemporalReasoning --> Transform
DTClassifier --> FeatureExtraction
CompModel --> CompAnalysis2

%% Apply engine styles
class Analysis,CompAnalysis,CompAnalysis2,SpatialAnalysis,TemporalReasoning,DecisionTree,DTClassifier,Modeling,CompModel,CompProps,DrawingMode,Pipeline,ASCIIProc,ContourDetection,FeatureExtraction,FloodFill,Transform engine;

%% Interface System Components
%% UI Components
GridWidget["ASCIIGridWidget\n(interface.ui.ascii_grid_widget)"]
DslGrid["DslGrid\n(interface.ui.dsl_grid)"]
CodeComposer["CodeCompositionEngine\n(interface.ui.code_composition)"]
TmplEngine["ComponentTemplateEngine\n(interface.ui.component_template)"]
PropEditor["PropertyEditor\n(interface.ui.property_editor)"]
ContentSwitch["ContentSwitcher\n(interface.ui.content_switcher)"]
TabbedContent["TabbedContent\n(interface.ui.tabbed_content)"]
Tabs["TabsManager\n(interface.ui.tabs)"]

%% API Components
AppController["ApplicationController\n(interface.api.application_controller)"]
UITranslator["ASCIIUITranslator\n(interface.api.ascii_ui_translation)"]
CLI["CommandLineInterface\n(interface.api.cli)"]
Visualizer["DslVisualizer\n(interface.api.dsl_visualizer)"]

%% Adapter Components
FrameworkAdapter["FrameworkAdapter\n(interface.adapters.framework_adapter)"]
TkAdapter["TkinterAdapter\n(interface.adapters.tkinter_adapter)"]
TkPlugin["TkinterPlugin\n(interface.adapters.tkinter_plugin)"]

%% Interface Internal Dependencies
%% UI Dependencies
GridWidget --> DslGrid
TabbedContent --> Tabs
TabbedContent --> ContentSwitch
PropEditor --> TmplEngine
CodeComposer --> TmplEngine

%% API Dependencies
AppController --> UITranslator
AppController --> Visualizer
CLI --> AppController
Visualizer --> GridWidget

%% Adapter Dependencies
FrameworkAdapter --> TkAdapter
TkAdapter --> TkPlugin
TkAdapter --> GridWidget
TkAdapter --> PropEditor
TkAdapter --> TabbedContent

%% Apply interface styles
class GridWidget,DslGrid,CodeComposer,TmplEngine,PropEditor,ContentSwitch,TabbedContent,Tabs,AppController,UITranslator,CLI,Visualizer,FrameworkAdapter,TkAdapter,TkPlugin ui;

%% Utils System Components
%% Core Utils
ASCIIUtils["ASCIIUtils\n(utils.ascii_utils)"]
DslUtils["DslUtils\n(utils.dsl_utils)"]
StorageProviders["StorageProviders\n(utils.storage_providers)"]

%% Plugin System
Plugin["Plugin\n(utils.plugin)"]
PluginManager["PluginManager\n(utils.plugin_manager)"]
ExtensionPoint["ExtensionPoint\n(utils.extension_point)"]

%% Cache System
CacheManager["CacheManager\n(utils.cache_manager)"]
CacheProvider["CacheProvider\n(utils.cache.provider)"]

%% Helpers
FuncRelManager["FunctionalRelationshipManager\n(utils.helpers.functional)"]
PerfMonitor["PerformanceMonitor\n(utils.helpers.performance)"]
QitiaAnalyzer["QitiaAnalyzer\n(utils.helpers.qitia)"]
SansiaImporter["SansiaImporter\n(utils.helpers.sansia)"]

%% Utils Internal Dependencies
%% Core Dependencies
DslUtils --> ASCIIUtils
StorageProviders --> CacheManager

%% Plugin Dependencies
PluginManager --> Plugin
PluginManager --> ExtensionPoint
Plugin --> ExtensionPoint

%% Cache Dependencies
CacheManager --> CacheProvider
CacheManager --> StorageProviders

%% Helper Dependencies
PerfMonitor --> PluginManager
QitiaAnalyzer --> FuncRelManager
SansiaImporter --> StorageProviders
FuncRelManager --> CacheManager

%% Apply utils styles
class ASCIIUtils,DslUtils,StorageProviders,Plugin,PluginManager,ExtensionPoint,CacheManager,CacheProvider,FuncRelManager,PerfMonitor,QitiaAnalyzer,SansiaImporter utils;

%% Testing Infrastructure
    subgraph Testing ["Testing System"]
        direction TB
        UnitTests["Unit Tests"]
        IntegTests["Integration Tests"]
        E2ETests["End-to-End Tests"]
        TestFixtures["Test Fixtures"]
        MockObjects["Mock Objects"]
        TestUtils["Test Utilities"]
    end

    %% Test Categories
    subgraph TestTypes ["Test Categories"]
        CoreTests["Core Tests"]
        DSLTests["DSL Tests"]
        RecogTests["Recognition Tests"]
        ModelTests["Modeling Tests"]
        GenTests["Generation Tests"]
        UITests["UI Tests"]
    end

    %% Test Dependencies
    UnitTests --> TestFixtures
    UnitTests --> MockObjects
    IntegTests --> TestFixtures
    E2ETests --> TestUtils

    %% Test Coverage
    CoreTests --> UnitTests
    DSLTests --> UnitTests
    RecogTests --> IntegTests
    ModelTests --> UnitTests
    GenTests --> E2ETests
    UITests --> E2ETests

    %% Style definitions
    classDef default fill:#f9f,stroke:#333,stroke-width:2px;
    classDef test fill:#e6ffe6,stroke:#333,stroke-width:2px;
    classDef fixture fill:#ffe6cc,stroke:#333,stroke-width:2px;

    class UnitTests,IntegTests,E2ETests test;
    class TestFixtures,MockObjects,TestUtils fixture;

%% Error Handling System
    subgraph ErrorSystem ["Error Handling System"]
        direction TB
        ErrorHandler["Error Handler"]
        ErrorRegistry["Error Registry"]
        ErrorLogger["Error Logger"]
        ErrorReporter["Error Reporter"]
        RecoveryManager["Recovery Manager"]
    end

    %% Error Types
    subgraph ErrorTypes ["Error Categories"]
        DSLErrors["DSL Errors"]
        ParseErrors["Parse Errors"]
        ValidationErrors["Validation Errors"]
        RuntimeErrors["Runtime Errors"]
        SystemErrors["System Errors"]
    end

    %% Error Flows
    DSLErrors --> ErrorHandler
    ParseErrors --> ErrorHandler
    ValidationErrors --> ErrorHandler
    RuntimeErrors --> ErrorHandler
    SystemErrors --> ErrorHandler

    ErrorHandler --> ErrorRegistry
    ErrorRegistry --> ErrorLogger
    ErrorRegistry --> ErrorReporter
    ErrorHandler --> RecoveryManager

    %% Recovery Actions
    RecoveryManager --> RetryAction["Retry Action"]
    RecoveryManager --> FallbackAction["Fallback Action"]
    RecoveryManager --> CleanupAction["Cleanup Action"]

    %% Style definitions
    classDef default fill:#f9f,stroke:#333,stroke-width:2px;
    classDef error fill:#ffe6e6,stroke:#333,stroke-width:2px;
    classDef handler fill:#e6f3ff,stroke:#333,stroke-width:2px;
    classDef action fill:#e6ffe6,stroke:#333,stroke-width:2px;

    class ErrorHandler,ErrorRegistry,ErrorLogger,ErrorReporter handler;
    class DSLErrors,ParseErrors,ValidationErrors,RuntimeErrors,SystemErrors error;
    class RetryAction,FallbackAction,CleanupAction action;

%% Persistence System
    subgraph Persistence ["Persistence System"]
        direction TB
        StorageManager["Storage Manager"]
        CacheSystem["Cache System"]
        FileStorage["File Storage"]
        StateManager["State Manager"]
        PersistenceUtils["Persistence Utils"]
    end

    %% Storage Types
    subgraph StorageTypes ["Storage Types"]
        PatternStorage["Pattern Storage"]
        ComponentStorage["Component Storage"]
        TemplateStorage["Template Storage"]
        ConfigStorage["Config Storage"]
        CacheStorage["Cache Storage"]
    end

    %% Storage Operations
    StorageManager --> FileStorage
    StorageManager --> CacheSystem
    StorageManager --> StateManager

    PatternStorage --> StorageManager
    ComponentStorage --> StorageManager
    TemplateStorage --> StorageManager
    ConfigStorage --> StorageManager
    CacheStorage --> CacheSystem

    %% Persistence Utils
    PersistenceUtils --> FileStorage
    PersistenceUtils --> CacheSystem
    StateManager --> PersistenceUtils

    %% Style definitions
    classDef default fill:#f9f,stroke:#333,stroke-width:2px;
    classDef storage fill:#e6f3ff,stroke:#333,stroke-width:2px;
    classDef manager fill:#ffe6cc,stroke:#333,stroke-width:2px;
    classDef utils fill:#e6ffe6,stroke:#333,stroke-width:2px;

    class StorageManager,StateManager manager;
    class FileStorage,CacheSystem,PatternStorage,ComponentStorage,TemplateStorage,ConfigStorage,CacheStorage storage;
    class PersistenceUtils utils;

%% Logging System
    subgraph Logging ["Logging System"]
        direction TB
        LogManager["Log Manager"]
        LogFormatter["Log Formatter"]
        LogRouter["Log Router"]
        LogFilter["Log Filter"]
        LogAnalyzer["Log Analyzer"]
    end

    %% Log Destinations
    subgraph LogDest ["Log Destinations"]
        FileLogger["File Logger"]
        ConsoleLogger["Console Logger"]
        MetricsLogger["Metrics Logger"]
        AlertLogger["Alert Logger"]
        DebugLogger["Debug Logger"]
    end

    %% Log Categories
    subgraph LogTypes ["Log Categories"]
        ErrorLogs["Error Logs"]
        InfoLogs["Info Logs"]
        DebugLogs["Debug Logs"]
        PerfLogs["Performance Logs"]
        AuditLogs["Audit Logs"]
    end

    %% Logging Flow
    ErrorLogs --> LogRouter
    InfoLogs --> LogRouter
    DebugLogs --> LogRouter
    PerfLogs --> LogRouter
    AuditLogs --> LogRouter

    LogRouter --> LogFilter
    LogFilter --> LogFormatter
    LogFormatter --> LogManager

    LogManager --> FileLogger
    LogManager --> ConsoleLogger
    LogManager --> MetricsLogger
    LogManager --> AlertLogger
    LogManager --> DebugLogger

    LogAnalyzer --> FileLogger
    LogAnalyzer --> MetricsLogger

    %% Style definitions
    classDef default fill:#f9f,stroke:#333,stroke-width:2px;
    classDef logger fill:#e6f3ff,stroke:#333,stroke-width:2px;
    classDef manager fill:#ffe6cc,stroke:#333,stroke-width:2px;
    classDef logtype fill:#e6ffe6,stroke:#333,stroke-width:2px;

    class LogManager,LogFormatter,LogRouter,LogFilter,LogAnalyzer manager;
    class FileLogger,ConsoleLogger,MetricsLogger,AlertLogger,DebugLogger logger;
    class ErrorLogs,InfoLogs,DebugLogs,PerfLogs,AuditLogs logtype;

%% Cross-module Dependencies
    %% Core <-> Recognition
    Pipeline --> RecognitionSystem
    FloodFill --> ASCIIGrid
    Contour --> ASCIIGrid
    ErrorHandler --> Recognition
    ASCIIGrid -.-> PatternMatch
    CompModel -.-> RuleEngine

    %% Core <-> Modeling
    Pipeline --> Modeling
    ContainAnalyzer --> CompModel
    LayoutAnalyzer --> CompModel
    RelationAnalyzer --> CompModel
    ErrorHandler --> Modeling
    CompModel -.-> SpatialAnalysis
    ASCIIGrid -.-> ModelBuilder

    %% Core <-> Generation
    Pipeline --> Generation
    Generator --> CompModel
    ErrorHandler --> Generation
    CompModel -.-> Templates
    ASCIIGrid -.-> CodeGenCore

    %% DSL <-> Core
    DslInterp --> Pipeline
    CmdDisp --> CompModel
    ErrorHandler --> DslInterp
    Pipeline -.-> CmdDisp
    ASCIIGrid -.-> DslInterp

    %% DSL <-> Recognition
    PatternDef --> PatternMatch
    PatternDef --> RuleEngine
    RuleEngine -.-> DslInterp
    PatternMatch -.-> Grammar

    %% DSL <-> Generation
    TmplEngine --> Templates
    PatternDef --> Generator
    Generator -.-> Grammar
    Templates -.-> PatternDef

    %% Plugin System Dependencies
    PluginMgr --> Pipeline
    ExtRegistry -.-> PatternDef
    ExtRegistry -.-> Generator
    ExtRegistry -.-> Features
    Pipeline -.-> PluginMgr
    Features -.-> ExtRegistry

    %% Recognition <-> Modeling
    Features --> Spatial
    RuleEngine --> ModelBuilder
    ModelBuilder -.-> PatternMatch
    Spatial -.-> RuleEngine

    %% Engine <-> Processing
    DecisionTree --> ClassProcessor
    TemporalReasoning --> NeuroAnalysis
    CompAnalysis --> CompMapping
    CompAnalysis2 --> NeuroAnalysis
    DTClassifier --> ClassProcessor
    ClassProcessor -.-> CompAnalysis
    NeuroAnalysis -.-> TemporalReasoning
    CompMapping -.-> CompAnalysis2

    %% Processing <-> Recognition
    ClassProcessor --> PatternMatch
    NeuroAnalysis --> Features
    CompMapping --> FloodFill
    PatternMatch -.-> NeuroAnalysis
    Features -.-> ClassProcessor
    FloodFill -.-> CompMapping

    %% Interface <-> Core
    GridWidget --> ASCIIGrid
    UITranslator --> Pipeline
    AppController --> CompModel
    ASCIIGrid -.-> UITranslator
    Pipeline -.-> AppController
    CompModel -.-> GridWidget

    %% Interface <-> Generation
    CodeComposer --> Generator
    TmplEngine --> CodeTemplate
    Generator -.-> UITranslator
    CodeTemplate -.-> TmplEngine

    %% Interface <-> Patterns
    GridWidget --> PatternMatcher
    PropEditor --> PropTemplate
    TkAdapter --> TkTemplate
    PatternMatcher -.-> PropEditor
    PropTemplate -.-> GridWidget
    TkTemplate -.-> TkAdapter

    %% Patterns <-> Processing
    PatternOptimizer --> ClassProcessor
    GridTransform --> CompMapping
    HierarchicalCluster --> NeuroAnalysis
    ClassProcessor -.-> HierarchicalCluster
    CompMapping -.-> PatternOptimizer
    NeuroAnalysis -.-> GridTransform

    %% Utils <-> Core
    ASCIIUtils --> ASCIIGrid
    DslUtils --> Pipeline
    CacheManager --> CompModel
    ASCIIGrid -.-> DslUtils
    Pipeline -.-> CacheManager
    CompModel -.-> ASCIIUtils

    %% Utils <-> Interface
    PerfMonitor --> GridWidget
    StorageProviders --> TkAdapter
    CacheManager --> UITranslator
    GridWidget -.-> CacheManager
    TkAdapter -.-> PerfMonitor
    UITranslator -.-> StorageProviders

    %% Utils <-> Engine
    CacheManager --> DecisionTree
    QitiaAnalyzer --> CompAnalysis
    SansiaImporter --> TemporalReasoning
    FuncRelManager --> CompAnalysis2
    DecisionTree -.-> QitiaAnalyzer
    CompAnalysis -.-> CacheManager
    TemporalReasoning -.-> SansiaImporter
    CompAnalysis2 -.-> FuncRelManager

    %% Utils <-> Patterns
    FuncRelManager --> PatternMatcher
    CacheProvider --> PatternRegistry
    PluginManager --> PatternOptimizer
    ExtensionPoint --> PatternDef
    PatternMatcher -.-> CacheProvider
    PatternRegistry -.-> PluginManager
    PatternOptimizer -.-> ExtensionPoint
    PatternDef -.-> FuncRelManager

    %% Style definitions
    classDef default fill:#f9f,stroke:#333,stroke-width:2px,color:#000000;
    classDef core fill:#e1f7d5,stroke:#333,stroke-width:2px,color:#000000;
    classDef dsl fill:#ffedcc,stroke:#333,stroke-width:2px,color:#000000;
    classDef recog fill:#f2e6ff,stroke:#333,stroke-width:2px,color:#000000;
    classDef model fill:#e6f3ff,stroke:#333,stroke-width:2px,color:#000000;
    classDef codegen fill:#ffe6e6,stroke:#333,stroke-width:2px,color:#000000;
    classDef plugin fill:#e6ffe6,stroke:#333,stroke-width:2px,color:#000000;
    classDef ui fill:#fff2e6,stroke:#333,stroke-width:2px,color:#000000;
    classDef utils fill:#e6e6e6,stroke:#333,stroke-width:2px,color:#000000;
    classDef processing fill:#fff0f9,stroke:#333,stroke-width:2px,color:#000000;
```
