from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm

from llm.llm import LLM


class ParallelLLM:
    """ A wrapper for an LLM that allows for parallel generation of responses to multiple prompts."""
    def __init__(self, llm: LLM):
        self._llm = llm

    def batch_generate(
        self,
        prompts: list[str],
        tools: list[list[dict]] | None = None,
        require_tool_call: bool = False,
    ):
        """Generate responses to multiple prompts concurrently, one thread per prompt.

        Args:
            prompts (list[str]): The input prompts to send to the LLM. At most 10 are allowed.
            tools (list[list[dict]] | None, optional): The tools available to the LLM for each prompt. Defaults to None.
            require_tool_call (bool, optional): If True, the LLM must respond with a tool call for every prompt. Defaults to False.

        Returns:
            list[LLMResponse]: The responses, in the same order as the prompts.

        Raises:
            ValueError: If tools and prompts differ in length, or if there are more than 10 prompts.
        """
        if tools is None:
            tools = [[] for _ in prompts]
        elif len(tools) != len(prompts):
            raise ValueError(
                "Length of tools list must match length of prompts list."
            )

        if len(prompts) > 10:
            raise ValueError(
                "Batch generation is limited to 10 prompts at a time to avoid overwhelming the LLM."
            )

        responses = [None] * len(prompts)

        with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
            futures = {
                executor.submit(self._llm.generate, prompt, tool, require_tool_call=require_tool_call): i
                for i, (prompt, tool) in enumerate(zip(prompts, tools))
            }

            with tqdm(
                total=len(prompts),
                desc="LLM Responses",
                unit="responses",
            ) as progress_bar:
                for future in as_completed(futures):
                    responses[futures[future]] = future.result()
                    progress_bar.update(1)

        return responses

    def __getattr__(self, name):
        return getattr(self._llm, name)