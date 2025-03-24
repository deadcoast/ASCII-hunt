class ProcessingPipeline:
    def __init__(self):
        self.processors = []
        self.context = {}
        self.error_handlers = {}
        self.performance_monitors = {}

    def register_processor(self, processor, stage_name):
        """Register a processor for a specific pipeline stage."""
        self.processors.append((stage_name, processor))

    def register_error_handler(self, stage_name, handler):
        """Register an error handler for a specific stage."""
        self.error_handlers[stage_name] = handler

    def register_performance_monitor(self, stage_name, monitor):
        """Register a performance monitor for a specific stage."""
        self.performance_monitors[stage_name] = monitor

    def process(self, input_data, context=None):
        """Process input data through the pipeline."""
        # Initialize or update context
        if context is not None:
            self.context.update(context)

        current_data = input_data
        stage_results = {}

        # Process through each stage
        for stage_name, processor in self.processors:
            try:
                # Start performance monitoring
                if stage_name in self.performance_monitors:
                    self.performance_monitors[stage_name].start()

                # Process data
                stage_result = processor.process(current_data, self.context)

                # End performance monitoring
                if stage_name in self.performance_monitors:
                    self.performance_monitors[stage_name].end()

                # Store result for this stage
                stage_results[stage_name] = stage_result

                # Update current data for next stage
                current_data = stage_result

            except Exception as e:
                # Handle error
                if stage_name in self.error_handlers:
                    handled_data = self.error_handlers[stage_name].handle_error(
                        e, current_data, self.context
                    )

                    if handled_data is not None:
                        # Continue with handled data
                        current_data = handled_data
                    else:
                        # Cannot continue pipeline
                        raise PipelineError(f"Error in stage {stage_name}: {str(e)}")
                else:
                    # No handler, propagate error
                    raise PipelineError(f"Error in stage {stage_name}: {str(e)}")

        # Return the final result and all stage results
        return current_data, stage_results

    def process_incremental(self, delta, context=None):
        """Process an incremental update through the pipeline."""
        # Initialize or update context
        if context is not None:
            self.context.update(context)

        current_delta = delta
        stage_results = {}

        # Process through each stage
        for stage_name, processor in self.processors:
            # Check if processor supports incremental updates
            if hasattr(processor, "process_incremental"):
                try:
                    # Start performance monitoring
                    if stage_name in self.performance_monitors:
                        self.performance_monitors[stage_name].start()

                    # Process delta
                    stage_result = processor.process_incremental(
                        current_delta, self.context
                    )

                    # End performance monitoring
                    if stage_name in self.performance_monitors:
                        self.performance_monitors[stage_name].end()

                    # Store result for this stage
                    stage_results[stage_name] = stage_result

                    # Update current delta for next stage
                    current_delta = stage_result

                except Exception as e:
                    # Handle error
                    if stage_name in self.error_handlers:
                        handled_delta = self.error_handlers[stage_name].handle_error(
                            e, current_delta, self.context
                        )

                        if handled_delta is not None:
                            # Continue with handled delta
                            current_delta = handled_delta
                        else:
                            # Cannot continue incremental update
                            raise PipelineError(
                                f"Error in incremental update for stage {stage_name}: {str(e)}"
                            )
                    else:
                        # No handler, propagate error
                        raise PipelineError(
                            f"Error in incremental update for stage {stage_name}: {str(e)}"
                        )
            else:
                # Processor doesn't support incremental updates, need to reprocess
                # This would retrieve the full data from context and process it
                full_data = self.context.get("current_data")
                if full_data is not None:
                    try:
                        # Start performance monitoring
                        if stage_name in self.performance_monitors:
                            self.performance_monitors[stage_name].start()

                        # Process full data
                        stage_result = processor.process(full_data, self.context)

                        # End performance monitoring
                        if stage_name in self.performance_monitors:
                            self.performance_monitors[stage_name].end()

                        # Store result for this stage
                        stage_results[stage_name] = stage_result

                        # Update current data for next stage
                        full_data = stage_result
                        self.context["current_data"] = full_data

                        # Create a new delta representing the full change
                        current_delta = {"type": "full_update", "data": full_data}

                    except Exception as e:
                        # Handle error
                        if stage_name in self.error_handlers:
                            handled_data = self.error_handlers[stage_name].handle_error(
                                e, full_data, self.context
                            )

                            if handled_data is not None:
                                # Continue with handled data
                                full_data = handled_data
                                self.context["current_data"] = full_data

                                # Create a new delta representing the full change
                                current_delta = {
                                    "type": "full_update",
                                    "data": full_data,
                                }
                            else:
                                # Cannot continue pipeline
                                raise PipelineError(
                                    f"Error in stage {stage_name}: {str(e)}"
                                )
                        else:
                            # No handler, propagate error
                            raise PipelineError(
                                f"Error in stage {stage_name}: {str(e)}"
                            )
                else:
                    # No full data available, cannot continue
                    raise PipelineError(
                        f"Cannot perform incremental update for stage {stage_name}: No full data available"
                    )

        # Return the final delta and all stage results
        return current_delta, stage_results


class PipelineError(Exception):
    """Exception raised for errors in the processing pipeline."""

    pass
