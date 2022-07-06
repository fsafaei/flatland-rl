import cProfile
import pstats

from flatland.core.env_observation_builder import DummyObservationBuilder
from flatland.envs.line_generators import sparse_line_generator
from flatland.envs.malfunction_generators import MalfunctionParameters, ParamMalfunctionGen
from flatland.envs.observations import TreeObsForRailEnv
from flatland.envs.predictions import ShortestPathPredictorForRailEnv
from flatland.envs.rail_env import RailEnv
from flatland.envs.rail_generators import sparse_rail_generator


def get_rail_env(nAgents=70, use_dummy_obs=False, width=60, height=60):
    # Rail Generator:

    num_cities = 5  # Number of cities to place on the map
    seed = 1  # Random seed
    max_rails_between_cities = 2  # Maximum number of rails connecting 2 cities
    max_rail_pairs_in_cities = 2  # Maximum number of pairs of tracks within a city
    # Even tracks are used as start points, odd tracks are used as endpoints)

    rail_generator = sparse_rail_generator(
        max_num_cities=num_cities,
        seed=seed,
        max_rails_between_cities=max_rails_between_cities,
        max_rail_pairs_in_city=max_rail_pairs_in_cities,
    )

    # Line Generator

    # sparse_line_generator accepts a dictionary which maps speeds to probabilities.
    # Different agent types (trains) with different speeds.
    speed_probability_map = {
        1.: 0.25,  # Fast passenger train
        1. / 2.: 0.25,  # Fast freight train
        1. / 3.: 0.25,  # Slow commuter train
        1. / 4.: 0.25  # Slow freight train
    }

    line_generator = sparse_line_generator(speed_probability_map)

    # Malfunction Generator:

    stochastic_data = MalfunctionParameters(
        malfunction_rate=1 / 10000,  # Rate of malfunction occurence
        min_duration=15,  # Minimal duration of malfunction
        max_duration=50  # Max duration of malfunction
    )

    malfunction_generator = ParamMalfunctionGen(stochastic_data)

    # Observation Builder

    # tree observation returns a tree of possible paths from the current position.
    max_depth = 3  # Max depth of the tree
    predictor = ShortestPathPredictorForRailEnv(
        max_depth=50)  # (Specific to Tree Observation - read code)

    observation_builder = TreeObsForRailEnv(
        max_depth=max_depth,
        predictor=predictor
    )

    if use_dummy_obs:
        observation_builder = DummyObservationBuilder()

    number_of_agents = nAgents  # Number of trains to create
    seed = 1  # Random seed

    env = RailEnv(
        width=width,
        height=height,
        rail_generator=rail_generator,
        line_generator=line_generator,
        number_of_agents=number_of_agents,
        random_seed=seed,
        obs_builder_object=observation_builder,
        malfunction_generator=malfunction_generator
    )
    return env


USE_PROFILER = True

PROFILE_CREATE = False
PROFILE_RESET = True
PROFILE_OBSERVATION = False

if __name__ == "__main__":
    print("Start ...")
    if USE_PROFILER:
        profiler = cProfile.Profile()

    print("Create env ... ")
    if PROFILE_CREATE:
        profiler.enable()
    env_fast = get_rail_env(nAgents=70, use_dummy_obs=True)
    if PROFILE_CREATE:
        profiler.disable()

    print("Reset env ... ")
    if PROFILE_RESET:
        profiler.enable()
    env_fast.reset(random_seed=1)
    if PROFILE_RESET:
        profiler.disable()

    print("Make actions ... ")
    action_dict = {agent.handle: 0 for agent in env_fast.agents}

    print("Step env ... ")
    env_fast.step(action_dict)

    if PROFILE_OBSERVATION:
        profiler.enable()

    print("get observation ... ")
    env_fast._get_observations()

    if PROFILE_OBSERVATION:
        profiler.disable()

    if USE_PROFILER:
        print("---- tottime")
        stats = pstats.Stats(profiler).sort_stats('tottime')  # ncalls, 'cumtime'...
        stats.print_stats(20)

        print("---- cumtime")
        stats = pstats.Stats(profiler).sort_stats('cumtime')  # ncalls, 'cumtime'...
        stats.print_stats(20)

        print("---- ncalls")
        stats = pstats.Stats(profiler).sort_stats('ncalls')  # ncalls, 'cumtime'...
        stats.print_stats(200)

    print("... end ")