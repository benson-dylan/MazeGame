if __name__ == "__main__":
    main_menu()
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font_path = "assets/fonts/DotGothic16-Regular.ttf"
    death_menu = DeathMenu(screen, font_path)
    action = death_menu.show()
    pygame.quit()

    if action == 'Retry':
        main_menu()
    else:
        sys.exit()