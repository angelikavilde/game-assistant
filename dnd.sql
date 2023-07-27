CREATE TABLE rarity(
    rarity_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rarity_name VARCHAR(15) UNIQUE NOT NULL);

INSERT INTO rarity(rarity_name) VALUES
    ('Common'), ('Uncommon'), ('Rare'), ('Very Rare'), ('Legendary'),
    ('Artifact'), ('Varies'), ('Unknown Rarity');

CREATE TABLE item_types (
    item_type_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_type_name VARCHAR(15) UNIQUE NOT NULL);

INSERT INTO item_types (item_type_name) VALUES
    ('Armour'), ('Potion'), ('Ring'), ('Rod'), ('Scroll'), ('Staff'),
    ('Wand'), ('Weapon'), ('Wondrous Item');

CREATE TABLE log_story(
    story_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    story VARCHAR(70));

CREATE INDEX date ON log_story (date_time);

CREATE TABLE characters(
    character_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    character_name TEXT NOT NULL,
    age SMALLINT,
    race VARCHAR(20) NOT NULL,
    class VARCHAR(20) NOT NULL);

CREATE TABLE players(
    user_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    character_id BIGINT,
    coins SMALLINT,
    FOREIGN KEY (character_id) REFERENCES characters(character_id));

CREATE INDEX player ON players(username, character_id);

CREATE TABLE magic_items(
    item_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    user_id SMALLINT,
    item_name VARCHAR(35) NOT NULL,
    item_type_id SMALLINT NOT NULL,
    rarity_id SMALLINT NOT NULL,
    attunement_req VARCHAR(3) NOT NULL,
    class VARCHAR(25),
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES players(user_id),
    FOREIGN KEY (rarity_id) REFERENCES rarity(rarity_id),
    FOREIGN KEY (item_type_id) REFERENCES item_types(item_type_id),
    CONSTRAINT attunement_req_only_yes_no CHECK (attunement_req IN ('yes','no')));

CREATE INDEX magic
    ON magic_items (user_id, rarity_id, item_type_id);
