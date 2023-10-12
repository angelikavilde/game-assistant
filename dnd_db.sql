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
    story VARCHAR(70),
    guild_id BIGINT);

CREATE INDEX date ON log_story (date_time);
CREATE INDEX guild ON log_story (guild_id);

CREATE TABLE players(
    user_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL);

CREATE INDEX player ON players(username);

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

CREATE INDEX magic ON magic_items (user_id, rarity_id, item_type_id, attunement_req, class, item_name);
